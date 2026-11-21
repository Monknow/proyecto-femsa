"""
Service layer for generating Executive and Technical PDF reports.

Uses reportlab to build the PDFs. 
"""

import io
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

import sys
from pathlib import Path as _Path
sys.path.append(str(_Path(__file__).resolve().parent.parent))

from core.db_connection import AsyncSessionLocal
from models.models import ServerModel, VulnerabilityModel
from models.report_schemas import ReportRequest

from contextlib import asynccontextmanager

from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from reportlab.platypus import Image


logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# Session helpers
# -------------------------------------------------------------------------

@asynccontextmanager
async def session_scope(db: Optional[AsyncSession] = None):
    """Yields the provided session, or creates a fresh one."""
    if db is not None:
        yield db
    else:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


def handle_db_error(e: Exception, operation: str) -> None:
    """Centralised error handler (read-only operations, no rollback needed)."""
    if isinstance(e, HTTPException):
        raise e
    elif isinstance(e, SQLAlchemyError):
        logger.error(f"SQLAlchemy error during '{operation}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while {operation}.",
        )
    else:
        logger.error(f"Unexpected error during '{operation}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while {operation}.",
        )


# -------------------------------------------------------------------------
# Data loading
# -------------------------------------------------------------------------

# Executive-report columns (map ORM attr → human-readable header)
EXEC_SERVER_COLUMNS: List[tuple[str, str]] = [
    ("os_family",          "Sistema Operativo"),
    ("infrastructure_type","Infraestructura"),
    ("functional_role",    "Rol Funcional"),
    ("environment",        "Environment"),
    ("region_group",       "Región"),
    ("asset_criticality",  "Criticalidad"),
    ("exposure_category",  "Exposure"),
    ("risk_band",          "Risk Band"),
]

EXEC_VULN_COLUMNS: List[tuple[str, str]] = [
    ("functional_category",       "Functional Category"),
    ("severity",                  "Severity"),
    ("finding_status",            "FindingStatus"),
    ("detection_frequency_band",  "DetectionFrequency"),
    ("remediation_category",      "RemediationCategory"),
    ("asset_criticality",         "AssetCriticality"),
]

# Technical-report columns – every column on each model, minus the FK that
# would duplicate the server_id already shown as a separate server row.
TECH_SERVER_COLUMNS: List[tuple[str, str]] = [
    ("_id",                       "ServerID"),
    ("os_family",                 "OSFamily"),
    ("os_lifecycle",              "OSLifecycle"),
    ("infrastructure_type",       "InfrastructureType"),
    ("asset_type",                "AssetType"),
    ("functional_role",           "FunctionalRole"),
    ("environment",               "Environment"),
    ("region_group",              "RegionGroup"),
    ("asset_criticality",         "AssetCriticality"),
    ("cpu_capacity_band",         "CPUCapacityBand"),
    ("memory_capacity_band",      "MemoryCapacityBand"),
    ("architecture_band",         "ArchitectureBand"),
    ("inventory_freshness_band",  "InventoryFreshnessBand"),
    ("boot_age_band",             "BootAgeBand"),
    ("exposure_category",         "ExposureCategory"),
    ("risk_band",                 "RiskBand"),
    ("vulnerability_volume_band", "VulnerabilityVolumeBand"),
]

TECH_VULN_COLUMNS: List[tuple[str, str]] = [
    ("_id",                       "VulnerabilityID"),
    ("server_id",                 "ServerID"),
    ("vulnerability_type_id",     "VulnerabilityTypeID"),
    ("functional_category",       "FunctionalCategory"),
    ("severity",                  "Severity"),
    ("finding_status",            "FindingStatus"),
    ("age_band",                  "AgeBand"),
    ("last_seen_band",            "LastSeenBand"),
    ("detection_frequency_band",  "DetectionFrequencyBand"),
    ("reopen_band",               "ReopenBand"),
    ("exploitability",            "Exploitability"),
    ("malware_association",       "MalwareAssociation"),
    ("compliance_flag",           "ComplianceFlag"),
    ("port_category",             "PortCategory"),
    ("protocol_category",         "ProtocolCategory"),
    ("encryption_context",        "EncryptionContext"),
    ("remediation_category",      "RemediationCategory"),
    ("slastatus",                 "SLAStatus"),
    ("asset_criticality",         "AssetCriticality"),
    ("finding_risk_band",         "FindingRiskBand"),
]


async def _fetch_servers(
    req: ReportRequest,
    session: AsyncSession,
) -> list:
    """Return a list of ServerModel ORM instances matching the request filters."""
    stmt = select(ServerModel)
    if req.server_ids:
        stmt = stmt.where(ServerModel._id.in_(req.server_ids))
    if req.limit:
        stmt = stmt.limit(req.limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def _fetch_vulnerabilities(
    req: ReportRequest,
    session: AsyncSession,
) -> list:
    """Return a list of VulnerabilityModel ORM instances matching the request filters."""
    stmt = select(VulnerabilityModel)
    if req.server_ids:
        stmt = stmt.where(VulnerabilityModel.server_id.in_(req.server_ids))
    if req.vulnerability_ids:
        stmt = stmt.where(VulnerabilityModel._id.in_(req.vulnerability_ids))
    if req.limit:
        stmt = stmt.limit(req.limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())



# -------------------------------------------------------------------------
# PDF construction helpers
# -------------------------------------------------------------------------

def _cell(value: Any) -> str:
    """Stringify a cell value for the PDF table, replacing None with '-'."""
    if value is None:
        return "-"
    return str(value)


def _build_table(headers: List[str], rows: List[List[str]]) -> Table:
    """Build a ReportLab Table with a styled header row."""
    # Truncate rows to avoid memory blow-up for enormous datasets
    MAX_ROWS = 5_000
    display_rows = rows[:MAX_ROWS]

    data = [headers] + display_rows
    col_count = len(headers)
    # Distribute width evenly across the page (LETTER width ≈ 8.5 in, with margins)
    available_width = LETTER[0] - 1.0 * inch  # leave 0.5 in margin each side
    col_width = available_width / col_count

    tbl = Table(data, colWidths=[col_width] * col_count, repeatRows=1, hAlign="LEFT")
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME",  (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",  (0, 0), (-1, 0), 7),
                ("FONTSIZE",  (0, 1), (-1, -1), 6),
                ("ALIGN",     (0, 0), (-1, -1), "LEFT"),
                ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING",    (0, 1), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 2),
                ("GRID",      (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
            ]
        )
    )

    if len(rows) > MAX_ROWS:
        # We will append a note after this table in the caller
        pass

    return tbl

# -------------------------------------------------------------------------
# Dashboard helpers 
# -------------------------------------------------------------------------

SEVERITY_COLORS = {
    "critical": "#D13438",
    "critica":  "#D13438",
    "crítica":  "#D13438",
    "high":     "#F7630C",
    "alta":     "#F7630C",
    "medium":   "#FFB900",
    "media":    "#FFB900",
    "low":      "#0078D4",
    "baja":     "#0078D4",
    "info":     "#737373",
}

SEVERITY_PRIORITY = {
    "critical": 0, "critica": 0, "crítica": 0,
    "high": 1, "alta": 1,
    "medium": 2, "media": 2,
    "low": 3, "baja": 3,
    "info": 4,
}


# --- Universal field extractors ------------------------------------------

def _get_field(obj: Any, attr: str, fallback: str = "Sin clasificar") -> str:
    """Safely extract any column from a ServerModel or VulnerabilityModel."""
    val = getattr(obj, attr, None)
    if val is None:
        return fallback
    text = str(val).strip()
    return text if text else fallback


def _get_severity(vuln: Any) -> str:
    """Read 'severity' from VulnerabilityModel, falling back to 'criticality'."""
    sev = _get_field(vuln, "severity", fallback="")
    if sev:
        return sev
    return _get_field(vuln, "criticality", fallback="Sin clasificar")


def _get_server_label(server: Any) -> str:
    """Return the best human-readable identifier for a server on chart axes."""
    for attr in ("hostname", "name", "ip_address", "_id"):
        label = _get_field(server, attr, fallback="")
        if label:
            return label
    return "Desconocido"


# --- Matplotlib -> ReportLab image helpers -------------------------------

def _fig_to_rl_image(fig: plt.Figure, width_in: float, height_in: float) -> Image:
    """Render a Matplotlib Figure at 300 DPI into a ReportLab Image flowable."""
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0.06)
    img_buf.seek(0)
    return Image(img_buf, width=width_in * inch, height=height_in * inch)


def _empty_chart_image(
    message: str,
    width_in: float = 3.42,
    height_in: float = 1.85,
) -> Image:
    """Render a clean placeholder card when a filter returns zero records."""
    fig, ax = plt.subplots(figsize=(4.6, 2.5))
    try:
        ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=10, color="#64748B")
        ax.axis("off")
        return _fig_to_rl_image(fig, width_in, height_in)
    finally:
        plt.close(fig)


# --- Chart builders ------------------------------------------------------

def _chart_severity_donut(severity_counts: Dict[str, int]) -> Image:
    """Power BI-style donut chart with total vulnerability count centered inside."""
    if not severity_counts:
        return _empty_chart_image("Sin datos de severidad")

    ordered = sorted(
        severity_counts.items(),
        key=lambda item: SEVERITY_PRIORITY.get(item[0].lower(), 99),
    )
    labels = [k.title() for k, _ in ordered]
    values = [v for _, v in ordered]
    total = sum(values)
    palette = [SEVERITY_COLORS.get(k.lower(), "#5C6BC0") for k, _ in ordered]

    fig, ax = plt.subplots(figsize=(4.6, 2.5))
    try:
        wedges, _ = ax.pie(
            values,
            colors=palette,
            startangle=90,
            counterclock=False,
            wedgeprops={"width": 0.38, "edgecolor": "white", "linewidth": 2.2},
        )
        ax.text(0, 0.08, f"{total:,}", ha="center", va="center", fontsize=16, fontweight="bold", color="#0F2942")
        ax.text(0, -0.22, "TOTAL", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#64748B")

        legend_labels = [
            f"{lbl}: {val} ({(val / total) * 100:.0f}%)"
            for lbl, val in zip(labels, values)
        ]
        ax.legend(
            wedges,
            legend_labels,
            loc="center left",
            bbox_to_anchor=(0.92, 0.5),
            frameon=False,
            fontsize=8.5,
            labelcolor="#1E293B",
        )
        ax.set_aspect("equal")
        fig.subplots_adjust(left=0.02, right=0.58, top=0.95, bottom=0.05)
        return _fig_to_rl_image(fig, width_in=3.42, height_in=1.85)
    finally:
        plt.close(fig)


def _chart_top_vuln_types(top_vulns: List[tuple[str, int]]) -> Image:
    """Horizontal Seaborn bar chart of the Top 5 most frequent vulnerability categories."""
    if not top_vulns:
        return _empty_chart_image("Sin hallazgos registrados")

    items = top_vulns[:5]
    labels = [name[:24] + ("…" if len(name) > 24 else "") for name, _ in items]
    values = [count for _, count in items]
    max_val = max(values)

    with sns.axes_style("whitegrid"):
        fig, ax = plt.subplots(figsize=(4.6, 2.5))
        try:
            sns.barplot(
                x=values,
                y=labels,
                ax=ax,
                color="#0284C7",
                edgecolor="none",
                height=0.58,
            )
            sns.despine(left=False, bottom=True, top=True, right=True)
            ax.xaxis.set_visible(False)
            ax.grid(False)
            ax.tick_params(axis="y", labelsize=8.5, colors="#1E293B")
            ax.spines["left"].set_color("#CBD5E1")
            ax.set_xlim(0, max_val * 1.22)

            for idx, val in enumerate(values):
                ax.text(
                    val + max_val * 0.03,
                    idx,
                    f"{val}",
                    va="center",
                    ha="left",
                    fontsize=8.5,
                    fontweight="bold",
                    color="#0F2942",
                )

            fig.tight_layout(pad=0.4)
            return _fig_to_rl_image(fig, width_in=3.42, height_in=1.85)
        finally:
            plt.close(fig)


def _chart_top_servers_bar(server_vuln_counts: List[tuple[str, int]]) -> Image:
    """Horizontal Seaborn bar chart showing the Top 5 most exposed servers."""
    if not server_vuln_counts:
        return _empty_chart_image("Sin servidores afectados")

    items = server_vuln_counts[:5]
    labels = [name[:20] + ("…" if len(name) > 20 else "") for name, _ in items]
    values = [count for _, count in items]
    max_val = max(values)

    with sns.axes_style("whitegrid"):
        fig, ax = plt.subplots(figsize=(4.6, 2.5))
        try:
            sns.barplot(
                x=values,
                y=labels,
                ax=ax,
                color="#0F2942",
                edgecolor="none",
                height=0.58,
            )
            sns.despine(left=False, bottom=True, top=True, right=True)
            ax.xaxis.set_visible(False)
            ax.grid(False)
            ax.tick_params(axis="y", labelsize=8.5, colors="#1E293B")
            ax.spines["left"].set_color("#CBD5E1")
            ax.set_xlim(0, max_val * 1.22)

            for idx, val in enumerate(values):
                ax.text(
                    val + max_val * 0.03,
                    idx,
                    f"{val}",
                    va="center",
                    ha="left",
                    fontsize=8.5,
                    fontweight="bold",
                    color="#0F2942",
                )

            fig.tight_layout(pad=0.4)
            return _fig_to_rl_image(fig, width_in=3.42, height_in=1.85)
        finally:
            plt.close(fig)


def _chart_server_posture_donut(servers: list, vulnerabilities: list) -> Image:
    """
    Cross-references servers and vulnerabilities to classify every server into:
    - Crítico / Alto (Red)
    - Medio / Bajo (Amber)
    - Sin Hallazgos (Green)
    """
    if not servers:
        return _empty_chart_image("Sin datos de servidores")

    worst_priority_by_server: Dict[Any, int] = {}
    for v in vulnerabilities:
        prio = SEVERITY_PRIORITY.get(_get_severity(v).lower(), 3)
        prev = worst_priority_by_server.get(v.server_id, 99)
        if prio < prev:
            worst_priority_by_server[v.server_id] = prio

    crit_high = 0
    med_low = 0
    clean = 0
    for s in servers:
        worst = worst_priority_by_server.get(s._id, 99)
        if worst in (0, 1):
            crit_high += 1
        elif worst < 99:
            med_low += 1
        else:
            clean += 1

    slices = [
        ("Crítico / Alto", crit_high, "#D13438"),
        ("Medio / Bajo",   med_low,   "#FFB900"),
        ("Sin Hallazgos",  clean,     "#107C10"),
    ]
    slices = [(lbl, val, col) for lbl, val, col in slices if val > 0]

    labels = [s[0] for s in slices]
    values = [s[1] for s in slices]
    palette = [s[2] for s in slices]
    total = len(servers)

    fig, ax = plt.subplots(figsize=(4.6, 2.5))
    try:
        wedges, _ = ax.pie(
            values,
            colors=palette,
            startangle=90,
            counterclock=False,
            wedgeprops={"width": 0.38, "edgecolor": "white", "linewidth": 2.2},
        )
        ax.text(0, 0.08, f"{total:,}", ha="center", va="center", fontsize=16, fontweight="bold", color="#0F2942")
        ax.text(0, -0.22, "SERVIDORES", ha="center", va="center", fontsize=6.5, fontweight="bold", color="#64748B")

        legend_labels = [
            f"{lbl}: {val} ({(val / total) * 100:.0f}%)"
            for lbl, val in zip(labels, values)
        ]
        ax.legend(
            wedges,
            legend_labels,
            loc="center left",
            bbox_to_anchor=(0.92, 0.5),
            frameon=False,
            fontsize=8.5,
            labelcolor="#1E293B",
        )
        ax.set_aspect("equal")
        fig.subplots_adjust(left=0.02, right=0.58, top=0.95, bottom=0.05)
        return _fig_to_rl_image(fig, width_in=3.42, height_in=1.85)
    finally:
        plt.close(fig)


# --- Dashboard grid layout helpers ---------------------------------------

def _build_kpi_row(kpis: List[tuple[str, str, str]]) -> Table:
    """Render a 4-column row of Power BI KPI cards: (value, label, hex_color)."""
    available_width = LETTER[0] - 1.0 * inch
    gap = 0.12 * inch
    card_width = (available_width - gap * (len(kpis) - 1)) / len(kpis)
    normal_style = getSampleStyleSheet()["Normal"]

    col_widths: List[float] = []
    cards: List[Any] = []

    for idx, (value, label, hex_color) in enumerate(kpis):
        if idx > 0:
            col_widths.append(gap)
            cards.append("")

        col_widths.append(card_width)
        inner = Table(
            [
                [Paragraph(f'<font size="16" color="{hex_color}"><b>{value}</b></font>', normal_style)],
                [Paragraph(f'<font size="7" color="#475569"><b>{label.upper()}</b></font>', normal_style)],
            ],
            colWidths=[card_width],
        )
        inner.setStyle(
            TableStyle(
                [
                    ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                    ("LINEABOVE",     (0, 0), (-1, 0),  3, colors.HexColor(hex_color)),
                    ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
                    ("TOPPADDING",    (0, 0), (-1, 0),  7),
                    ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
                ]
            )
        )
        cards.append(inner)

    wrapper = Table([cards], colWidths=col_widths)
    wrapper.setStyle(
        TableStyle(
            [
                ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                ("TOPPADDING",    (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return wrapper


def _build_two_chart_row(
    left_title: str,
    left_img: Image,
    right_title: str,
    right_img: Image,
) -> Table:
    """Place two chart cards side-by-side in a bordered 2-column grid."""
    available_width = LETTER[0] - 1.0 * inch
    gap = 0.16 * inch
    card_w = (available_width - gap) / 2
    normal_style = getSampleStyleSheet()["Normal"]

    grid = Table(
        [
            [
                Paragraph(f'<font size="9" color="#0F2942"><b>{left_title}</b></font>', normal_style),
                "",
                Paragraph(f'<font size="9" color="#0F2942"><b>{right_title}</b></font>', normal_style),
            ],
            [left_img, "", right_img],
        ],
        colWidths=[card_w, gap, card_w],
    )
    grid.setStyle(
        TableStyle(
            [
                ("BOX",           (0, 0), (0, 1), 0.5, colors.HexColor("#CBD5E1")),
                ("BOX",           (2, 0), (2, 1), 0.5, colors.HexColor("#CBD5E1")),
                ("BACKGROUND",    (0, 0), (0, 1), colors.white),
                ("BACKGROUND",    (2, 0), (2, 1), colors.white),
                ("TOPPADDING",    (0, 0), (-1, 0), 7),
                ("LEFTPADDING",   (0, 0), (-1, -1), 7),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 5),
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return grid


# -------------------------------------------------------------------------
# Core class
# -------------------------------------------------------------------------

class ReportGenerator:
    """
    Generates Executive or Technical PDF reports from database data.

    Usage:
        gen = ReportGenerator()
        pdf_bytes = await gen.generate(request, db_session)
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(
            ParagraphStyle(
                name="SectionHeading",
                parent=self.styles["Heading2"],
                spaceAfter=10,
                spaceBefore=18,
                textColor=colors.HexColor("#003366"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="ReportSubtitle",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.grey,
                spaceAfter=20,
            )
        )

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def generate(
        self,
        req: ReportRequest,
        db: Optional[AsyncSession] = None,
    ) -> bytes:
        """
        Generates the requested PDF report and returns the raw PDF bytes.

        Returns:
            bytes – the complete PDF file content (application/pdf).
        """
        logger.info(f"Generating '{req.report_type}' report…")
        try:
            async with session_scope(db) as session:
                servers = await _fetch_servers(req, session)
                vulnerabilities = await _fetch_vulnerabilities(req, session)

            logger.info(
                f"Loaded {len(servers)} server(s), {len(vulnerabilities)} vulnerability(ies) for report."
            )

            if req.report_type == "executive":
                pdf_bytes = self._build_executive(servers, vulnerabilities)
            else:
                pdf_bytes = self._build_technical(servers, vulnerabilities)

            logger.info(f"PDF generated successfully ({len(pdf_bytes)} bytes).")
            return pdf_bytes

        except HTTPException:
            raise
        except Exception as e:
            handle_db_error(e, f"generating {req.report_type} report")




    # ------------------------------------------------------------------
    # Executive report
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Executive report (Power BI-style Dashboard)
    # ------------------------------------------------------------------

    def _build_executive(self, servers: list, vulnerabilities: list) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=LETTER,
            topMargin=0.4 * inch,
            bottomMargin=0.4 * inch,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
        )
        story: list = []
        available_width = LETTER[0] - 1.0 * inch

        # 1. Executive Header Banner
        banner = Table(
            [
                [
                    Paragraph(
                        '<font size="14" color="#FFFFFF"><b>REPORTE EJECUTIVO DE CIBERSEGURIDAD</b></font>',
                        self.styles["Normal"],
                    )
                ],
                [
                    Paragraph(
                        f'<font size="8.5" color="#CBD5E1">Generado: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}  |  '
                        f'Alcance: {len(servers)} servidor(es) y {len(vulnerabilities)} hallazgo(s)</font>',
                        self.styles["Normal"],
                    )
                ],
            ],
            colWidths=[available_width],
        )
        banner.setStyle(
            TableStyle(
                [
                    ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#0F2942")),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
                    ("TOPPADDING",    (0, 0), (-1, 0),  10),
                    ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
                ]
            )
        )
        story.append(banner)
        story.append(Spacer(1, 10))

        # 2. Aggregate Metrics from Both Sheets
        severity_counter = Counter(_get_severity(v) for v in vulnerabilities)
        critical_high_count = sum(
            count
            for sev, count in severity_counter.items()
            if SEVERITY_PRIORITY.get(sev.lower(), 99) in (0, 1)
        )

        open_count = sum(
            1
            for v in vulnerabilities
            if _get_field(v, "status", "").lower()
            in ("open", "abierta", "abierto", "active", "activa", "pending", "pendiente")
        )

        server_name_map = {s._id: _get_server_label(s) for s in servers}
        vulns_per_server = Counter(
            server_name_map.get(v.server_id, str(v.server_id))
            for v in vulnerabilities
        )
        affected_servers_count = len(vulns_per_server)

        # 3. Top 4 KPI Cards
        kpis = [
            (str(len(servers)), "Servidores Evaluados", "#0F2942"),
            (str(len(vulnerabilities)), "Total Vulnerabilidades", "#0284C7"),
            (str(critical_high_count), "Críticas y Altas", "#D13438"),
            (
                f"{affected_servers_count}/{len(servers)}" if servers else "0",
                "Servidores Afectados",
                "#F7630C",
            ),
        ]
        story.append(_build_kpi_row(kpis))
        story.append(Spacer(1, 10))

        # 4. Automated Executive Takeaway Callout
        if vulnerabilities:
            top_srv, top_srv_count = vulns_per_server.most_common(1)[0]
            crit_pct = round((critical_high_count / len(vulnerabilities)) * 100)
            open_note = (
                f" Actualmente <b>{open_count}</b> hallazgo(s) permanecen en estado abierto."
                if open_count > 0
                else ""
            )
            summary_text = (
                f"<b>Síntesis Ejecutiva:</b> Se detectaron <b>{len(vulnerabilities)}</b> vulnerabilidades "
                f"en <b>{affected_servers_count}</b> de <b>{len(servers)}</b> servidores evaluados. "
                f"El <b>{crit_pct}%</b> ({critical_high_count}) corresponde a severidad <b>Crítica o Alta</b>, "
                f"concentrándose la mayor exposición en <b>{top_srv}</b> ({top_srv_count} hallazgos)."
                f"{open_note}"
            )
        else:
            summary_text = (
                "<b>Síntesis Ejecutiva:</b> No se registraron vulnerabilidades bajo los filtros aplicados."
            )

        callout = Table(
            [
                [
                    Paragraph(
                        f'<font size="8.5" color="#1E293B">{summary_text}</font>',
                        self.styles["Normal"],
                    )
                ]
            ],
            colWidths=[available_width],
        )
        callout.setStyle(
            TableStyle(
                [
                    ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#EEF4FA")),
                    ("LINEBEFORE",    (0, 0), (0, -1),  3.5, colors.HexColor("#0284C7")),
                    ("TOPPADDING",    (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(callout)
        story.append(Spacer(1, 10))

        # 5. Visual Row 1: Panorama de Vulnerabilidades
        vuln_category_counter = Counter(
            _get_field(v, "category", "Sin categoría") for v in vulnerabilities
        )
        story.append(
            _build_two_chart_row(
                left_title="Distribución por Severidad",
                left_img=_chart_severity_donut(dict(severity_counter)),
                right_title="Top 5 Categorías más Frecuentes",
                right_img=_chart_top_vuln_types(vuln_category_counter.most_common(5)),
            )
        )
        story.append(Spacer(1, 10))

        # 6. Visual Row 2: Exposición de Servidores
        story.append(
            _build_two_chart_row(
                left_title="Top 5 Servidores con Mayor Exposición",
                left_img=_chart_top_servers_bar(vulns_per_server.most_common(5)),
                right_title="Estado de Riesgo por Servidor",
                right_img=_chart_server_posture_donut(servers, vulnerabilities),
            )
        )
        story.append(Spacer(1, 12))

        # 7. Top 5 Priority Vulnerabilities Table (using EXEC_VULN_COLUMNS)
        story.append(Paragraph("Top 5 Hallazgos Prioritarios", self.styles["SectionHeading"]))
        if vulnerabilities:
            sorted_vulns = sorted(
                vulnerabilities,
                key=lambda v: SEVERITY_PRIORITY.get(_get_severity(v).lower(), 99),
            )[:5]
            headers = [h for _, h in EXEC_VULN_COLUMNS]
            rows = [
                [_cell(getattr(v, attr, None)) for attr, _ in EXEC_VULN_COLUMNS]
                for v in sorted_vulns
            ]
            story.append(_build_table(headers, rows))
        else:
            story.append(Paragraph("No hay datos de vulnerabilidades.", self.styles["Normal"]))

        # 8. Top 5 Most Exposed Servers Table (using EXEC_SERVER_COLUMNS)
        story.append(Paragraph("Top 5 Servidores Críticos", self.styles["SectionHeading"]))
        if servers:
            raw_server_counts = Counter(v.server_id for v in vulnerabilities)
            sorted_servers = sorted(
                servers,
                key=lambda s: raw_server_counts.get(s._id, 0),
                reverse=True,
            )[:5]
            headers = [h for _, h in EXEC_SERVER_COLUMNS]
            rows = [
                [_cell(getattr(s, attr, None)) for attr, _ in EXEC_SERVER_COLUMNS]
                for s in sorted_servers
            ]
            story.append(_build_table(headers, rows))
        else:
            story.append(Paragraph("No hay datos de servidores.", self.styles["Normal"]))

        doc.build(story)
        return buf.getvalue()

    # ------------------------------------------------------------------
    # Technical report
    # ------------------------------------------------------------------

    def _build_technical(self, servers: list, vulnerabilities: list) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=LETTER,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
        )
        story: list = []

        # Title
        story.append(Paragraph("Reporte Técnico", self.styles["Title"]))
        story.append(
            Paragraph(
                f"Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                self.styles["ReportSubtitle"],
            )
        )

        # ---- Servers (all columns) ----------------------------------------
        story.append(Paragraph("Servidores — Detalle Completo", self.styles["SectionHeading"]))
        if servers:
            headers = [h for _, h in TECH_SERVER_COLUMNS]
            rows = [
                [_cell(getattr(s, attr, None)) for attr, _ in TECH_SERVER_COLUMNS]
                for s in servers
            ]
            story.append(_build_table(headers, rows))
        else:
            story.append(Paragraph("No hay datos de servidores.", self.styles["Normal"]))
        story.append(Spacer(1, 14))

        # ---- Vulnerabilities (all columns) --------------------------------
        story.append(Paragraph("Vulnerabilidades — Detalle Completo", self.styles["SectionHeading"]))
        if vulnerabilities:
            headers = [h for _, h in TECH_VULN_COLUMNS]
            rows = [
                [_cell(getattr(v, attr, None)) for attr, _ in TECH_VULN_COLUMNS]
                for v in vulnerabilities
            ]
            story.append(_build_table(headers, rows))
        else:
            story.append(
                Paragraph("No hay datos de vulnerabilidades.", self.styles["Normal"])
            )

        doc.build(story)
        return buf.getvalue()

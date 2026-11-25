"""
Service layer for generating Executive and Technical PDF reports.

"""

import io
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
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
import matplotlib.patches as mpatches
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
SERVER_COLS = {
    "server_id":         "_id",
    "os":                "os_family",
    "infrastructure":    "infrastructure_type",
    "asset_type":        "asset_type",
    "role":              "functional_role",
    "environment":       "environment",
    "region":            "region_group",
    "asset_criticality": "asset_criticality",
    "exposure":          "exposure_category",
    "risk_level":        "risk_band",
}

VULN_COLS = {
    "finding_id":        "_id",
    "server_id":         "server_id",
    "category":          "functional_category",
    "severity":          "severity",            
    "status":            "finding_status",
    "reopen":            "reopen_band",
    "exploitability":    "exploitability",
    "malware":           "malware_association",
    "compliance":        "compliance_flag",
    "port_type":         "port_category",
    "protocol_type":     "protocol_category",
    "encryption":        "encryption_context",         
    "remediation_type":  "remediation_category",
    "criticality":       "asset_criticality",
    "risk":              "finding_risk_band",
}


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
    MAX_ROWS = 5_000
    display_rows = rows[:MAX_ROWS]

    data = [headers] + display_rows
    col_count = len(headers)
    available_width = LETTER[0] - 1.0 * inch
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
    return tbl


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

SEVERITY_CONFIG: Dict[str, Tuple[str, int, str]] = {
    "4": ("Critical", 0, "#E11D48"),  "4.0": ("Critical", 0, "#E11D48"), 
    "3": ("High",     1, "#F97316"),  "3.0": ("High",     1, "#F97316"),  
    "2": ("Medium",   2, "#FACC15"),  "2.0": ("Medium",   2, "#FACC15"),  
    "1": ("Low",      3, "#3B82F6"),  "1.0": ("Low",      3, "#3B82F6"),  
}

POSITIVE_FLAGS = {
    "yes", "no", "YES", "NO", "known_or_available", "associated"
}

ASSET_CRIT_PRIORITY = {
    "very_high": 0,
    "high":      1,
    "medium":    2,
    "low":       3,
}

DARK_BG = "#0B0F19"
CARD_BG = "#121826"
CARD_BORDER = "#1F2937"
TEXT_PRIMARY = "#F8FAFC"
TEXT_MUTED = "#94A3B8"


# -------------------------------------------------------------------------
# Field extraction helpers 
# -------------------------------------------------------------------------

def _read_col(obj: Any, col_name: str, fallback: str = "") -> str:
    if obj is None:
        return fallback
    val = getattr(obj, col_name, None)
    if val is None and hasattr(obj, "__dict__"):
        val = obj.__dict__.get(col_name)
    if val is None:
        return fallback
    text = str(val).strip()
    return text if text and text.lower() not in {"none", "nan", "null"} else fallback


def _norm_severity(raw: str) -> Tuple[str, int, str]:
    key = raw.strip().lower()
    if key in SEVERITY_CONFIG:
        return SEVERITY_CONFIG[key]
    return (raw.strip().title() if raw.strip() else "Sin clasificar", 99, "#818CF8")


def _norm_region(raw: str) -> str:
    txt = raw.strip().lower()
    if "region_north" in txt:
        return "Norte"
    if "region_central" in txt:
        return "Central"
    if "region_south" in txt:
        return "Sur"
    return "Sin región"


def _is_positive_flag(raw: str) -> bool:
    txt = raw.strip().lower()
    if not txt or txt in {"not_identified"}:
        return False
    return txt in POSITIVE_FLAGS or any(word in txt for word in ("associated","known_or_available"))


# -------------------------------------------------------------------------
# 3. Graphing helpers
# -------------------------------------------------------------------------


def _fig_to_rl_image(fig: plt.Figure, width_in: float, height_in: float) -> Image:
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0.05)
    img_buf.seek(0)
    return Image(img_buf, width=width_in * inch, height=height_in * inch)


def _dark_empty_chart(msg: str, w_in: float, h_in: float) -> Image:
    fig, ax = plt.subplots(figsize=(w_in * 1.35, h_in * 1.35))
    try:
        fig.patch.set_facecolor(CARD_BG)
        ax.set_facecolor(CARD_BG)
        ax.text(0.5, 0.5, msg, ha="center", va="center", color=TEXT_MUTED, fontsize=8.5)
        ax.axis("off")
        return _fig_to_rl_image(fig, width_in=w_in, height_in=h_in)
    finally:
        plt.close(fig)


def _chart_regional_dominant_map(region_sev_matrix: Dict[str, Counter]) -> Image:
    """
    North/Central/South map with bubbles showing:
    - The number inside the bubble is the total number of findings in that region
    - The color inside the bubble is the dominant severity 
    """
    fig, ax = plt.subplots(figsize=(4.8, 4.9))
    try:
        fig.patch.set_facecolor(CARD_BG)
        ax.set_facecolor("#090D16")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

        blobs = [
            mpatches.Ellipse((3.3, 7.4), width=4.8, height=2.8, angle=-18, facecolor="#1A2234", edgecolor="#263147", lw=1),
            mpatches.Ellipse((5.3, 4.8), width=3.5, height=2.4, angle=-25, facecolor="#1A2234", edgecolor="#263147", lw=1),
            mpatches.Ellipse((7.3, 2.5), width=3.5, height=2.2, angle=12,  facecolor="#1A2234", edgecolor="#263147", lw=1),
        ]
        for b in blobs:
            ax.add_patch(b)

        coords = {
            "Norte":   (3.2, 7.5),
            "Central": (5.2, 4.9),
            "Sur":     (7.2, 2.6),
        }

        for reg, (x, y) in coords.items():
            sev_counts = region_sev_matrix.get(reg, Counter())
            total = sum(sev_counts.values())

            if total == 0:
                dom_label = "Sin hallazgos"
                bubble_color = "#475569"
            else:
                dom_label = sorted(
                    sev_counts.items(),
                    key=lambda item: (-item[1], _norm_severity(item[0])[1]),
                )[0][0]
                _, _, bubble_color = _norm_severity(dom_label)

            # Halo luminoso + círculo principal
            ax.scatter([x], [y], s=1400, color=bubble_color, alpha=0.25, zorder=3)
            ax.scatter([x], [y], s=540, color=bubble_color, edgecolors="#F8FAFC", linewidths=1.4, zorder=4)
            ax.text(x, y, f"{total:,}", ha="center", va="center", color="white", fontsize=10.5, fontweight="bold", zorder=5)

            ax.text(
                x, y - 0.92, f"{reg.upper()} • Dom: {dom_label}",
                ha="center", va="top", color=TEXT_PRIMARY, fontsize=7.8, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#1E293B", edgecolor=bubble_color, lw=0.9),
                zorder=5,
            )

        legend_items = [
            mpatches.Patch(color="#E11D48", label="Critical"),
            mpatches.Patch(color="#F97316", label="High"),
            mpatches.Patch(color="#FACC15", label="Medium"),
            mpatches.Patch(color="#3B82F6", label="Low"),
        ]
        ax.legend(
            handles=legend_items, loc="lower center", frameon=False,
            fontsize=7.2, labelcolor=TEXT_MUTED, ncol=4, bbox_to_anchor=(0.5, 0.01),
            handlelength=1.0, columnspacing=0.8,
        )

        fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.05)
        return _fig_to_rl_image(fig, width_in=3.32, height_in=3.34)
    finally:
        plt.close(fig)


def _chart_stacked_severity_bars(dim_sev_matrix: Dict[str, Counter], empty_msg: str) -> Image:
    """
    Horizontal stacked bars by Severity (Critical, High, Medium, Low).
    Shows which Category, Infrastructure or OS has the most risk and volume.
    """
    if not dim_sev_matrix:
        return _dark_empty_chart(empty_msg, 3.08, 1.45)

    def _rank_key(item):
        _, c = item
        crit_high = c.get("Critical", 0) + c.get("High", 0)
        return (crit_high, sum(c.values()))

    top_items = sorted(dim_sev_matrix.items(), key=_rank_key, reverse=True)[:5][::-1]
    labels = [k[:15] + ("…" if len(k) > 15 else "") for k, _ in top_items]
    sev_levels = [("Critical", "#E11D48"), ("High", "#F97316"), ("Medium", "#FACC15"), ("Low", "#3B82F6")]

    fig, ax = plt.subplots(figsize=(4.2, 2.05))
    try:
        fig.patch.set_facecolor(CARD_BG)
        ax.set_facecolor(CARD_BG)

        lefts = [0] * len(top_items)
        for sev_name, sev_color in sev_levels:
            vals = [c.get(sev_name, 0) for _, c in top_items]
            if any(vals):
                ax.barh(labels, vals, left=lefts, color=sev_color, height=0.56, label=sev_name)
                lefts = [l + v for l, v in zip(lefts, vals)]

        max_total = max(lefts) if lefts else 1
        ax.set_xlim(0, max_total * 1.18)
        for idx, total in enumerate(lefts):
            ax.text(total + max_total * 0.025, idx, f"{total:,}", va="center", ha="left",
                    color=TEXT_PRIMARY, fontsize=7.5, fontweight="bold")

        ax.tick_params(axis="y", colors=TEXT_MUTED, labelsize=7.8, length=0)
        ax.tick_params(axis="x", bottom=False, labelbottom=False)
        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.legend(
            loc="lower center", bbox_to_anchor=(0.45, -0.22), ncol=4, frameon=False,
            fontsize=6.8, labelcolor=TEXT_MUTED, handlelength=0.9, columnspacing=0.7,
        )
        fig.subplots_adjust(left=0.30, right=0.95, top=0.95, bottom=0.22)
        return _fig_to_rl_image(fig, width_in=3.08, height_in=1.45)
    finally:
        plt.close(fig)


def _chart_env_malware_exploit(env_stats: Dict[str, Dict[str, int]]) -> Image:
    """
    Horizontal grouped bars by Environment showing:
    - Findings with detected Malware (Neon Pink)
    - Findings Exploitable (Yellow)
    """
    if not env_stats:
        return _dark_empty_chart("Sin datos de entornos", 3.08, 1.45)

    top_envs = sorted(
        env_stats.items(),
        key=lambda x: (x[1]["malware"] + x[1]["exploitable"], x[1]["total"]),
        reverse=True,
    )[:5][::-1]

    labels = [k[:14] for k, _ in top_envs]
    malware_vals = [v["malware"] for _, v in top_envs]
    exploit_vals = [v["exploitable"] for _, v in top_envs]
    y_pos = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(4.2, 2.05))
    try:
        fig.patch.set_facecolor(CARD_BG)
        ax.set_facecolor(CARD_BG)

        ax.barh([y + 0.17 for y in y_pos], malware_vals, height=0.32, color="#F472B6", label="Con Malware")
        ax.barh([y - 0.17 for y in y_pos], exploit_vals, height=0.32, color="#FACC15", label="Explotables")

        max_v = max(malware_vals + exploit_vals + [1])
        ax.set_xlim(0, max_v * 1.22)
        for y, m_v, e_v in zip(y_pos, malware_vals, exploit_vals):
            ax.text(m_v + max_v * 0.025, y + 0.17, str(m_v), va="center", color="#F472B6", fontsize=7, fontweight="bold")
            ax.text(e_v + max_v * 0.025, y - 0.17, str(e_v), va="center", color="#FACC15", fontsize=7, fontweight="bold")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, color=TEXT_MUTED, fontsize=7.8)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", bottom=False, labelbottom=False)
        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.legend(
            loc="lower center", bbox_to_anchor=(0.45, -0.22), ncol=2, frameon=False,
            fontsize=7, labelcolor=TEXT_MUTED, handlelength=1.0,
        )
        fig.subplots_adjust(left=0.28, right=0.95, top=0.95, bottom=0.22)
        return _fig_to_rl_image(fig, width_in=3.08, height_in=1.45)
    finally:
        plt.close(fig)

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

    def _build_executive(self, servers: list, vulnerabilities: list) -> bytes:
        buf = io.BytesIO()
        page_size = landscape(LETTER)
        doc = SimpleDocTemplate(
            buf,
            pagesize=page_size,
            leftMargin=0.32 * inch,
            rightMargin=0.32 * inch,
            topMargin=0.26 * inch,
            bottomMargin=0.26 * inch,
        )

        def _paint_dark_canvas(canvas, _doc):
            canvas.saveState()
            canvas.setFillColor(colors.HexColor(DARK_BG))
            canvas.rect(0, 0, page_size[0], page_size[1], fill=1, stroke=0)
            canvas.restoreState()

        title_st = ParagraphStyle("DkTitle", fontName="Helvetica-Bold", fontSize=13.5, textColor=colors.HexColor(TEXT_PRIMARY))
        sub_st = ParagraphStyle("DkSub", fontName="Helvetica", fontSize=7.8, textColor=colors.HexColor(TEXT_MUTED))
        kpi_lbl_st = ParagraphStyle("KpiLbl", fontName="Helvetica-Bold", fontSize=6.8, textColor=colors.HexColor(TEXT_MUTED))
        kpi_val_st = ParagraphStyle("KpiVal", fontName="Helvetica-Bold", fontSize=16, textColor=colors.HexColor(TEXT_PRIMARY))
        card_hdr_st = ParagraphStyle("CardHdr", fontName="Helvetica-Bold", fontSize=8.2, textColor=colors.HexColor(TEXT_PRIMARY))
        tbl_hdr_st = ParagraphStyle("TblHdr", fontName="Helvetica-Bold", fontSize=6.5, textColor=colors.HexColor(TEXT_MUTED))
        tbl_cell_st = ParagraphStyle("TblCell", fontName="Helvetica", fontSize=6.8, textColor=colors.HexColor("#CBD5E1"))

        # -----------------------------------------------------------------
        # 1. Index servers by server_id
        # -----------------------------------------------------------------
        server_map: Dict[str, Any] = {}
        for s in servers:
            sid = _read_col(s, SERVER_COLS["server_id"])
            if not sid:
                sid = _read_col(s, "_id") or _read_col(s, "id")
            if sid:
                server_map[sid] = s

        region_sev_matrix: Dict[str, Counter] = {"Norte": Counter(), "Central": Counter(), "Sur": Counter()}
        cat_sev_matrix: Dict[str, Counter] = {}
        infra_sev_matrix: Dict[str, Counter] = {}
        os_sev_matrix: Dict[str, Counter] = {}
        env_stats: Dict[str, Dict[str, int]] = {}

        impacted_server_ids = set()
        critical_high_count = 0
        exploitable_count = 0
        malware_count = 0
        enriched_findings = []

        # -----------------------------------------------------------------
        # 2. Process vulnerabilities and merge with server data
        # -----------------------------------------------------------------
        for v in vulnerabilities:
            sid = _read_col(v, VULN_COLS["server_id"])
            srv = server_map.get(sid)
            if sid:
                impacted_server_ids.add(sid)

            raw_sev = (
                _read_col(v, VULN_COLS["severity"])
                or _read_col(v, VULN_COLS["criticality"])
                or _read_col(srv, SERVER_COLS["risk_level"], "Sin clasificar")
            )
            sev_label, sev_prio, sev_color = _norm_severity(raw_sev)
            if sev_prio in (0, 1):
                critical_high_count += 1

            category = _read_col(v, VULN_COLS["category"], "Sin categoría")
            finding_id = _read_col(v, VULN_COLS["finding_id"]) or _read_col(v, "_id", "-")
            has_malware = _is_positive_flag(_read_col(v, VULN_COLS["malware"]))
            is_exploitable = _is_positive_flag(_read_col(v, VULN_COLS["exploitability"]))

            if has_malware:
                malware_count += 1
            if is_exploitable:
                exploitable_count += 1

            region = _norm_region(_read_col(srv, SERVER_COLS["region"]) or _read_col(v, "regional_group"))
            infra = _read_col(srv, SERVER_COLS["infrastructure"], "Sin infra")
            os_name = _read_col(srv, SERVER_COLS["os"], "Sin OS")
            env = _read_col(srv, SERVER_COLS["environment"], "Sin entorno")
            asset_crit = _read_col(srv, SERVER_COLS["asset_criticality"], "N/A")

            if region in region_sev_matrix:
                region_sev_matrix[region][sev_label] += 1

            cat_sev_matrix.setdefault(category, Counter())[sev_label] += 1
            infra_sev_matrix.setdefault(infra, Counter())[sev_label] += 1
            os_sev_matrix.setdefault(os_name, Counter())[sev_label] += 1

            env_bucket = env_stats.setdefault(env, {"total": 0, "malware": 0, "exploitable": 0})
            env_bucket["total"] += 1
            if has_malware:
                env_bucket["malware"] += 1
            if is_exploitable:
                env_bucket["exploitable"] += 1

            asset_crit_prio = ASSET_CRIT_PRIORITY.get(asset_crit.lower(), 99)
            enriched_findings.append({
                "finding_id": finding_id,
                "server_id": sid or "-",
                "sev_label": sev_label,
                "sev_prio": sev_prio,
                "sev_color": sev_color,
                "os": os_name,
                "infra": infra,
                "env": env,
                "category": category,
                "asset_crit": asset_crit,
                "asset_crit_prio": asset_crit_prio,
                "has_malware": has_malware,
                "is_exploitable": is_exploitable,
            })

        story = []

        hdr_tbl = Table(
            [[
                Paragraph("REPORTE EJECUTIVO DE RIESGOS Y EXPOSICIÓN", title_st),
                Paragraph(
                    f"Servidores: {len(servers):,} | Hallazgos: {len(vulnerabilities):,} | {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                    ParagraphStyle("R", parent=sub_st, alignment=TA_RIGHT),
                ),
            ]],
            colWidths=[6.6 * inch, 3.76 * inch],
        )
        hdr_tbl.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        story.append(hdr_tbl)
        story.append(Spacer(1, 6))

        # -----------------------------------------------------------------
        # 3. 4 KPIs: Total Findings, Critical/High, Exploitable, Malware
        # -----------------------------------------------------------------
        kpi_specs = [
            ("TOTAL HALLAZGOS / ACTIVOS", f"{len(vulnerabilities):,} <font size='9' color='#94A3B8'>({len(impacted_server_ids):,} srv)</font>", "#818CF8"),
            ("SEVERIDAD CRITICAL / HIGH", f"{critical_high_count:,}", "#E11D48"),
            ("HALLAZGOS EXPLOTABLES", f"{exploitable_count:,}", "#FACC15"),
            ("CON MALWARE DETECTADO", f"{malware_count:,}", "#F472B6"),
        ]
        kpi_cells = []
        for lbl, val, accent in kpi_specs:
            mini = Table([[Paragraph(lbl, kpi_lbl_st)], [Paragraph(val, kpi_val_st)]], colWidths=[2.30 * inch])
            mini.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(CARD_BG)),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(CARD_BORDER)),
                ("LINEABOVE", (0, 0), (-1, 0), 2.2, colors.HexColor(accent)),
                ("TOPPADDING", (0, 0), (-1, 0), 5),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ]))
            kpi_cells.append(mini)

        kpi_row = Table(
            [[kpi_cells[0], "", kpi_cells[1], "", kpi_cells[2], "", kpi_cells[3]]],
            colWidths=[2.48 * inch, 0.14 * inch, 2.48 * inch, 0.14 * inch, 2.48 * inch, 0.14 * inch, 2.50 * inch],
        )
        kpi_row.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(kpi_row)
        story.append(Spacer(1, 8))

        # -----------------------------------------------------------------
        # 4. Regional map + stacked bars for Category, Infrastructure, OS, Environment
        # -----------------------------------------------------------------
        def _wrap_card(title: str, img: Image, col_w: float) -> Table:
            card = Table([[Paragraph(title, card_hdr_st)], [img]], colWidths=[col_w])
            card.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(CARD_BG)),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(CARD_BORDER)),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]))
            return card

        map_card = _wrap_card(
            "Postura Regional (Color = Riesgo Predominante)",
            _chart_regional_dominant_map(region_sev_matrix),
            3.48 * inch,
        )
        cat_card = _wrap_card(
            "Severidad por Categoría (Top 5)",
            _chart_stacked_severity_bars(cat_sev_matrix, "Sin categorías"),
            3.29 * inch,
        )
        infra_card = _wrap_card(
            "Severidad por Infraestructura",
            _chart_stacked_severity_bars(infra_sev_matrix, "Sin infraestructura"),
            3.29 * inch,
        )
        os_card = _wrap_card(
            "Severidad por Sistema Operativo (OS)",
            _chart_stacked_severity_bars(os_sev_matrix, "Sin datos de OS"),
            3.29 * inch,
        )
        env_card = _wrap_card(
            "Malware y Explotabilidad por Entorno",
            _chart_env_malware_exploit(env_stats),
            3.29 * inch,
        )

        bento_grid = Table(
            [
                [map_card, "", cat_card, "", infra_card],
                ["",       "", os_card,  "", env_card],
            ],
            colWidths=[3.50 * inch, 0.14 * inch, 3.29 * inch, 0.14 * inch, 3.29 * inch],
        )
        bento_grid.setStyle(TableStyle([
            ("SPAN", (0, 0), (0, 1)),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, 0), 0), ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
            ("TOPPADDING", (0, 1), (-1, 1), 0), ("BOTTOMPADDING", (0, 1), (-1, 1), 0),
        ]))
        story.append(bento_grid)
        story.append(Spacer(1, 8))

        # -----------------------------------------------------------------
        # Top 7 findings by priority: Critical/High, Exploitable, Malware, Asset Criticality
        # -----------------------------------------------------------------
        priority_list = sorted(
            enriched_findings,
            key=lambda x: (
                not x["has_malware"],
                not x["is_exploitable"],
                x["sev_prio"],
                x["asset_crit_prio"],
            ),
        )[:7]

        headers = [
            Paragraph(h, tbl_hdr_st)
            for h in ["SERVIDOR", "SEVERIDAD", "CATEGORÍA", "SISTEMA OP.", "INFRAESTRUCTURA", "ENTORNO", "CRIT. ACTIVO", "MALWARE", "EXPLOTABLE"]
        ]
        rows = [headers]

        for item in priority_list:
            mal_badge = "<font color='#F472B6'><b>SÍ</b></font>" if item["has_malware"] else "<font color='#64748B'>No</font>"
            exp_badge = "<font color='#FACC15'><b>SÍ</b></font>" if item["is_exploitable"] else "<font color='#64748B'>No</font>"
            rows.append([
                Paragraph(f"<font color='#818CF8'><b>{item['server_id'][:16]}</b></font>", tbl_cell_st),
                Paragraph(f"<font color='{item['sev_color']}'><b>{item['sev_label'].upper()}</b></font>", tbl_cell_st),
                Paragraph(item["category"][:22], tbl_cell_st),
                Paragraph(item["os"][:15], tbl_cell_st),
                Paragraph(item["infra"][:16], tbl_cell_st),
                Paragraph(item["env"][:13], tbl_cell_st),
                Paragraph(item["asset_crit"][:12], tbl_cell_st),
                Paragraph(mal_badge, tbl_cell_st),
                Paragraph(exp_badge, tbl_cell_st),
            ])

        telemetry_tbl = Table(
            rows,
            colWidths=[1.10 * inch, 0.90 * inch, 1.78 * inch, 1.15 * inch, 1.25 * inch, 1.05 * inch, 1.03 * inch, 1.00 * inch, 1.10 * inch],
        )
        telemetry_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(CARD_BG)),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(CARD_BORDER)),
            ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor(CARD_BORDER)),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(telemetry_tbl)

        doc.build(story, onFirstPage=_paint_dark_canvas, onLaterPages=_paint_dark_canvas)
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

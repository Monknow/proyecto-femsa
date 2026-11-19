"""
Service layer for generating Executive and Technical PDF reports.

Uses reportlab to build the PDFs.  The service follows the
same patterns used elsewhere in the codebase: async functions, session_scope,
handle_db_error, and SQLAlchemy select() queries.
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

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# Session helpers (mirrors db_service_retrival / db_service_population)
# -------------------------------------------------------------------------

from contextlib import asynccontextmanager


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
        story.append(Paragraph("Reporte Ejecutivo", self.styles["Title"]))
        story.append(
            Paragraph(
                f"Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                self.styles["ReportSubtitle"],
            )
        )

        # ---- Servidores ---------------------------------------------------
        story.append(Paragraph("Servidores", self.styles["SectionHeading"]))
        if servers:
            headers = [h for _, h in EXEC_SERVER_COLUMNS]
            rows = [
                [_cell(getattr(s, attr, None)) for attr, _ in EXEC_SERVER_COLUMNS]
                for s in servers
            ]
            story.append(_build_table(headers, rows))
        else:
            story.append(Paragraph("No hay datos de servidores.", self.styles["Normal"]))
        story.append(Spacer(1, 14))

        # ---- Vulnerabilidades ---------------------------------------------
        story.append(Paragraph("Vulnerabilidades", self.styles["SectionHeading"]))
        if vulnerabilities:
            headers = [h for _, h in EXEC_VULN_COLUMNS]
            rows = [
                [_cell(getattr(v, attr, None)) for attr, _ in EXEC_VULN_COLUMNS]
                for v in vulnerabilities
            ]
            story.append(_build_table(headers, rows))
        else:
            story.append(
                Paragraph("No hay datos de vulnerabilidades.", self.styles["Normal"])
            )

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

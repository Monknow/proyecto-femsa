"""
Router for PDF report generation (Executive & Technical).

POST /reports  → returns the generated PDF as a streaming download.
"""

from pathlib import Path
import sys

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.db_connection import get_db
from models.report_schemas import ReportRequest
from services.report_service import ReportGenerator

router = APIRouter(prefix="/reports", tags=["Reports"])


# Single shared instance (stateless, safe to reuse)
_generator = ReportGenerator()


@router.post(
    "/",
    summary="Generate a PDF report",
    description=(
        "Generates an **executive** or **technical** PDF report based on the "
        "current database contents.  Optionally filter by server IDs, "
        "vulnerability IDs, or cap the row count with `limit`."
    ),
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "The generated PDF file.",
        }
    },
)
async def generate_report(
    req: ReportRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Accepts a JSON body with ``report_type`` (``"executive"`` or ``"technical"``)
    and optional filters, then returns the PDF as a downloadable binary response.
    """
    pdf_bytes: bytes = await _generator.generate(req, db)

    filename = f"{req.report_type}_report.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )

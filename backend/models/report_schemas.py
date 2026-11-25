from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """Optional filters the caller may supply when requesting a report."""
    report_type: Literal["executive", "technical"] = Field(
        ...,
        description="Which report to generate: 'executive' (high-level summary) or 'technical' (full dump).",
    )
    server_ids: Optional[List[str]] = Field(
        None,
        description="Only include these Server IDs. If omitted, all servers are included.",
    )
    vulnerability_ids: Optional[List[str]] = Field(
        None,
        description="Only include these Vulnerability IDs. If omitted, all vulnerabilities are included.",
    )
    limit: Optional[int] = Field(
        None,
        gt=0,
        description="Cap the number of rows per entity (useful for large databases).",
    )

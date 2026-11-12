from datetime import datetime
import inspect
import io
import logging
from pathlib import Path
import sys
from typing import BinaryIO, Optional, Tuple, Union

from fastapi import Depends, File, HTTPException, UploadFile, status
import pandas as pd
import pandera.pandas as pa
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.db_connection import get_db
from models.df_schemas import ServerDataFrameSchema, VulnerabilityDataFrameSchema, FileMetadataDataFrameSchema
from models.api_schemas import FileMetadataField, ServerField, VulnerabilityField, AggregationData

logger = logging.getLogger(__name__)

import xxhash

def chunk_list(data, chunk_size=1000):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def compute_file_hash(content: bytes) -> str:
    return xxhash.xxh64(content).hexdigest()


def _detect_header_row(
    excel_file: pd.ExcelFile, sheet_name: str, candidate_cols: list[str]
) -> int:
    """
    Scans the first 10 rows of a sheet to locate the true column header row
    by matching known column names (case-insensitive). Returns the row index
    to use as the `header` argument for pd.read_excel. Defaults to 0.
    """
    try:
        preview = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, nrows=10)
        for idx, row in preview.iterrows():
            row_vals = [str(val).strip().lower() for val in row.values if pd.notna(val)]
            if any(col.lower() in row_vals for col in candidate_cols):
                return int(idx)
    except Exception:
        pass
    return 0


def _extract_bytes_and_name(
    file_source: Union[UploadFile, bytes, BinaryIO, str, Path],
    file_name: Optional[str] = None,
    file_bytes: Optional[bytes] = None,
) -> Tuple[bytes, str]:
    """
    Extracts raw bytes and filename from various file source types.
    """
    # 1. Determine bytes
    if file_bytes is not None:
        content = file_bytes
    elif isinstance(file_source, bytes):
        content = file_source
    elif isinstance(file_source, UploadFile):
        file_source.file.seek(0)
        content = file_source.file.read()
        file_source.file.seek(0)
    elif isinstance(file_source, (str, Path)):
        with open(file_source, "rb") as f:
            content = f.read()
    elif hasattr(file_source, "read"):
        if hasattr(file_source, "seek"):
            file_source.seek(0)
        content = file_source.read()
        if hasattr(file_source, "seek"):
            file_source.seek(0)
    else:
        raise ValueError(f"Unsupported file source type: {type(file_source)}")

    # 2. Determine filename
    if file_name:
        name = file_name
    elif isinstance(file_source, UploadFile) and file_source.filename:
        name = file_source.filename
    elif isinstance(file_source, (str, Path)):
        name = Path(file_source).name
    else:
        name = "uploaded_file.xlsx"

    return content, name


# -------------------------------------------------------------------------
# 1. Sheet & Schema Validation Function
# -------------------------------------------------------------------------

def validate_excel_sheets(
    file_source: Union[UploadFile, bytes, BinaryIO, str, Path]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Reads an Excel file source, locates 'Servers' and 'Vulnerabilities' sheets,
    and validates them against their Pandera schemas.

    Args:
        file_source: UploadFile, bytes, file-like stream, or file path.

    Returns:
        A tuple containing (servers_df, vulnerabilities_df).

    Raises:
        HTTPException (400): If opening the Excel fails, required sheets are missing,
                             or schema validation fails.
    """
    logger.info("Validating Excel file sheets and schemas...")

    content, _ = _extract_bytes_and_name(file_source)

    try:
        excel_file = pd.ExcelFile(io.BytesIO(content))
        sheets = excel_file.sheet_names

        # Case-insensitive fuzzy match for sheets
        server_sheet = next(
            (s for s in sheets if "server" in s.lower() or "servidor" in s.lower()),
            None,
        )
        vulnerability_sheet = next(
            (s for s in sheets if "vulnerab" in s.lower()), None
        )

        if not server_sheet or not vulnerability_sheet:
            missing = [
                s
                for s, found in [
                    ("Servers", server_sheet),
                    ("Vulnerabilities", vulnerability_sheet),
                ]
                if not found
            ]
            logger.warning(f"Missing required sheet(s): {missing}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required sheet(s) in the Excel file: {', '.join(missing)}",
            )

        # Detect true header rows in case of top banner/blank rows
        header_server = _detect_header_row(
            excel_file, server_sheet, ["serverid", "osfamily"]
        )
        header_vuln = _detect_header_row(
            excel_file, vulnerability_sheet, ["findingid", "vulnerabilityid"]
        )

        servers_df = pd.read_excel(
            excel_file, sheet_name=server_sheet, header=header_server
        )
        vulnerabilities_df = pd.read_excel(
            excel_file, sheet_name=vulnerability_sheet, header=header_vuln
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to open or parse Excel file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to open or parse the Excel file: {str(e)}",
        )

    # Standardize column aliases if present in dataset (e.g. FindingID -> VulnerabilityID)
    if (
        "FindingID" in vulnerabilities_df.columns
        and "VulnerabilityID" not in vulnerabilities_df.columns
    ):
        vulnerabilities_df = vulnerabilities_df.rename(
            columns={"FindingID": "VulnerabilityID"}
        )
    if (
        "ExploitabilityCategory" in vulnerabilities_df.columns
        and "Exploitability" not in vulnerabilities_df.columns
    ):
        vulnerabilities_df = vulnerabilities_df.rename(
            columns={"ExploitabilityCategory": "Exploitability"}
        )

    # Map string boolean values in ComplianceFlag (e.g. YES/NO/SI) to boolean
    if "ComplianceFlag" in vulnerabilities_df.columns:
        bool_map = {
            "yes": True,
            "no": False,
            "true": True,
            "false": False,
            "si": True,
            "1": True,
            "0": False,
        }
        vulnerabilities_df["ComplianceFlag"] = vulnerabilities_df[
            "ComplianceFlag"
        ].apply(
            lambda x: bool_map.get(str(x).strip().lower(), None)
            if pd.notna(x) and not isinstance(x, bool)
            else x
        )

    schema_errors = []

    # Validate Servers DataFrame
    try:
        servers_df = ServerDataFrameSchema.validate(servers_df, lazy=True)
    except pa.errors.SchemaErrors as err:
        errors_summary = err.failure_cases[
            ["column", "check", "error_type"]
        ].to_dict(orient="records")
        schema_errors.append(f"Servers Sheet Errors: {errors_summary}")

    # Validate Vulnerabilities DataFrame
    try:
        vulnerabilities_df = VulnerabilityDataFrameSchema.validate(
            vulnerabilities_df, lazy=True
        )
    except pa.errors.SchemaErrors as err:
        errors_summary = err.failure_cases[
            ["column", "check", "error_type"]
        ].to_dict(orient="records")
        schema_errors.append(f"Vulnerabilities Sheet Errors: {errors_summary}")

    if schema_errors:
        logger.warning(f"Excel content failed schema validation: {schema_errors}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Excel file content failed schema validation.",
                "errors": schema_errors,
            },
        )

    logger.info(
        f"Validation successful. Servers: {len(servers_df)} rows, Vulnerabilities: {len(vulnerabilities_df)} rows."
    )
    return servers_df, vulnerabilities_df


# -------------------------------------------------------------------------
# 2. File Metadata Generation Function
# -------------------------------------------------------------------------

def generate_file_metadata(
    file_source: Union[UploadFile, bytes, BinaryIO, str, Path],
    servers_df: pd.DataFrame,
    vulnerabilities_df: pd.DataFrame,
    file_name: Optional[str] = None,
    file_bytes: Optional[bytes] = None,
) -> pd.DataFrame:
    """
    Inspects the file content and validated DataFrames to generate file metadata
    as specified in the FileMetadata model, returned as a 1-row pd.DataFrame.

    Fields:
        - _id: File content hash (xxhash / sha256)
        - file_name: File name
        - size_mb: File size in megabytes
        - upload_date: Current datetime
        - records: Number of vulnerabilities in file
        - new_vulnerabilities: Count of FindingStatus in ['NEW', 'REOPENED']
        - fixed_vulnerabilities: Count of FindingStatus == 'REMEDIATED'
        - updated_vulnerabilities: List of unique VulnerabilityID strings
        - updated_servers: List of unique ServerID strings

    Returns:
        pd.DataFrame: A 1-row DataFrame containing the metadata fields.
    """
    logger.info("Generating file metadata from validated sheets...")

    content, resolved_file_name = _extract_bytes_and_name(
        file_source=file_source, file_name=file_name, file_bytes=file_bytes
    )

    # Identifier via hash
    file_id = compute_file_hash(content)

    # Size in megabytes
    size_mb = round(len(content) / (1024 * 1024), 4)

    # Current upload date
    upload_date = datetime.utcnow()

    # Total vulnerability records
    records = len(vulnerabilities_df)

    # New and fixed vulnerabilities calculation based on FindingStatus
    new_vulnerabilities = 0
    fixed_vulnerabilities = 0
    if "FindingStatus" in vulnerabilities_df.columns:
        status_clean = (
            vulnerabilities_df["FindingStatus"]
            .astype(str)
            .str.strip()
            .str.lower()
        )
        new_vulnerabilities = int(status_clean.isin(["new", "reopened"]).sum())
        fixed_vulnerabilities = int((status_clean == "remediated").sum())

    # ID lists
    updated_vulnerabilities = (
        vulnerabilities_df["VulnerabilityID"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
        if "VulnerabilityID" in vulnerabilities_df.columns
        else []
    )
    updated_servers = (
        servers_df["ServerID"].dropna().astype(str).unique().tolist()
        if "ServerID" in servers_df.columns
        else []
    )

    metadata_dict = {
        "_id": file_id,
        "file_name": resolved_file_name,
        "size_mb": size_mb,
        "upload_date": upload_date,
        "records": records,
        "new_vulnerabilities": new_vulnerabilities,
        "fixed_vulnerabilities": fixed_vulnerabilities,
        "updated_vulnerabilities": updated_vulnerabilities,
        "updated_servers": updated_servers,
    }

    metadata_df = pd.DataFrame([metadata_dict])
    logger.info(
        f"File metadata generated successfully: _id={file_id}, records={records}, "
        f"new={new_vulnerabilities}, fixed={fixed_vulnerabilities}"
    )
    return metadata_df


# -------------------------------------------------------------------------
# 3. Final Encapsulated Function (FastAPI Dependency)
# -------------------------------------------------------------------------

async def process_excel_upload(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    FastAPI dependency that receives an uploaded .xlsx file directly,
    validates the servers and vulnerabilities sheets, generates file metadata,
    and returns a tuple of 3 DataFrames: (servers_df, vulnerabilities_df, metadata_df).

    Can be injected directly into any endpoint via Depends(process_excel_upload).
    """
    logger.info(f"Processing uploaded file: '{getattr(file, 'filename', 'unknown')}'...")

    if hasattr(file, "read"):
        if inspect.iscoroutinefunction(file.read):
            content = await file.read()
            if hasattr(file, "seek") and inspect.iscoroutinefunction(file.seek):
                await file.seek(0)
            elif hasattr(file, "seek"):
                file.seek(0)
        else:
            content = file.file.read() if hasattr(file, "file") else file.read()
            if hasattr(file, "seek"):
                file.seek(0)
    else:
        content = file

    # Validate sheets and extract DataFrames
    servers_df, vulnerabilities_df = validate_excel_sheets(content)

    # Generate File Metadata DataFrame
    metadata_df = generate_file_metadata(
        file_source=file,
        servers_df=servers_df,
        vulnerabilities_df=vulnerabilities_df,
        file_name=file.filename,
        file_bytes=content,
    )

    return servers_df, vulnerabilities_df, metadata_df


def validate_file(
    file_source: Union[UploadFile, bytes, BinaryIO, str, Path]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Synchronous validation function that reads an Excel file source, validates
    servers and vulnerabilities sheets, generates metadata, and returns 3 DataFrames.
    """
    servers_df, vulnerabilities_df = validate_excel_sheets(file_source)
    metadata_df = generate_file_metadata(
        file_source=file_source,
        servers_df=servers_df,
        vulnerabilities_df=vulnerabilities_df,
    )
    
    return servers_df, vulnerabilities_df, metadata_df

def vuln_aggregate_by(column: VulnerabiltyField) -> AggregationData:
    pass

def server_aggregate_by(column: ServerField) -> AggregationData:
    pass

def filemetadata_aggregate_by(column: FileMetadataField) -> AggregationData:
    pass
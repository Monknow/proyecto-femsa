from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys
from typing import Optional, Union

from fastapi import HTTPException, status
import pandas as pd
from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

sys.path.append(str(Path(__file__).resolve().parent.parent))
from models.df_schemas import VulnerabilityDataFrameSchema, FileMetadataDataFrameSchema, ServerDataFrameSchema
from models.models import VulnerabilityModel, ServerModel, FileMetadataModel
from core.db_connection import AsyncSessionLocal
from models.api_schemas import (
    FileMetadataListResponse,
    FileMetadataResponse,
    ServerListResponse,
    ServerResponse,
    VulnerabilityListResponse,
    VulnerabilityResponse,
    StatusResponse
)
from models.db_schemas import FileMetadata, Server, Vulnerability
from models.models import (
    FileMetadataModel,
    ServerModel,
    VulnerabilityModel,
    file_servers_association,
    file_vulnerabilities_association,
)
from utils.file_uploads import chunk_list as chunk_list

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# Centralized Error Handling & Session Scope Helper
# -------------------------------------------------------------------------

async def handle_db_error(e: Exception, operation: str, db = None) -> None:
    """
    Centralized error handler for db_service operations.
    Preserves HTTPExceptions with appropriate logging, logs unexpected or
    SQLAlchemy errors with full traceback, and raises proper HTTPExceptions.
    """
    
    if db is not None:
        try:
            await db.rollback()
        except Exception as rb_err:
            print(f"Failed to rollback session: {rb_err}")

    print(f"DB Error during {operation}: {str(e)}")
    
    if isinstance(e, HTTPException):
        logger.warning(
            f"HTTPException during '{operation}' (status_code={e.status_code}): {e.detail}"
        )
        raise e
    elif isinstance(e, SQLAlchemyError):
        logger.error(
            f"SQLAlchemy database error during '{operation}': {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred while {operation}.",
        )
    else:
        logger.error(
            f"Unexpected error during '{operation}': {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while {operation}.",
        )


@asynccontextmanager
async def session_scope(db: Optional[AsyncSession] = None):
    """
    Context manager that yields the provided AsyncSession if available,
    or creates, manages, and closes a new AsyncSession from AsyncSessionLocal.
    """
    if db is not None:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
    else:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


async def load_dataframes_to_db(
    server_df: ServerDataFrameSchema, 
    vulnerability_df: VulnerabilityDataFrameSchema,
    file_metadata_df: FileMetadataDataFrameSchema,
    db: Optional[AsyncSession] = None
) -> StatusResponse:
    logger.info("Starting load_dataframes_to_db operation...")
    try:
        server_records = ServerModel.sanitize_convert_df(server_df)
        vuln_records = VulnerabilityModel.sanitize_convert_df(vulnerability_df)
        file_meta_records, f_df = FileMetadataModel.sanitize_convert_df(file_metadata_df)

        

        # Prepare Association Records
        file_server_records = []
        file_vuln_records = []
        for _, row in f_df.iterrows():
            file_id = row.get("_id")
            if not file_id:
                continue
            server_ids = row.get("updated_servers") or []
            for sid in server_ids:
                if sid:
                    file_server_records.append({"file_id": str(file_id), "server_id": str(sid)})

            vuln_ids = row.get("updated_vulnerabilities") or []
            for vid in vuln_ids:
                if vid:
                    file_vuln_records.append({"file_id": str(file_id), "vulnerability_id": str(vid)})

        logger.info(
            f"Prepared data: {len(server_records)} servers, "
            f"{len(vuln_records)} vulnerabilities, "
            f"{len(file_meta_records)} file metadata records, "
            f"{len(file_server_records)} file-server links, "
            f"{len(file_vuln_records)} file-vulnerability links."
        )

        async with session_scope(db) as session:

            # Upsert Servers (Parent Table) in batches
            if server_records:
                stmt_servers = pg_insert(ServerModel)
                update_cols_servers = {
                    col.name: getattr(stmt_servers.excluded, col.name)
                    for col in ServerModel.__table__.columns
                    if not col.primary_key
                }
                upsert_servers = stmt_servers.on_conflict_do_update(
                    index_elements=[ServerModel._id],
                    set_=update_cols_servers
                )
                for batch in chunk_list(server_records, 1000):
                    await session.execute(upsert_servers, batch)

            # Upsert Vulnerabilities (Foreign Key to Servers) in batches
            if vuln_records:
                stmt_vulns = pg_insert(VulnerabilityModel)
                update_cols_vulns = {
                    col.name: getattr(stmt_vulns.excluded, col.name)
                    for col in VulnerabilityModel.__table__.columns
                    if not col.primary_key
                }
                upsert_vulns = stmt_vulns.on_conflict_do_update(
                    index_elements=[VulnerabilityModel._id],
                    set_=update_cols_vulns
                )
                for batch in chunk_list(vuln_records, 1000):
                    await session.execute(upsert_vulns, batch)

            # Upsert File Metadata in batches
            if file_meta_records:
                stmt_meta = pg_insert(FileMetadataModel)
                update_cols_meta = {
                    col.name: getattr(stmt_meta.excluded, col.name)
                    for col in FileMetadataModel.__table__.columns
                    if not col.primary_key
                }
                upsert_meta = stmt_meta.on_conflict_do_update(
                    index_elements=[FileMetadataModel._id],
                    set_=update_cols_meta
                )
                for batch in chunk_list(file_meta_records, 1000):
                    await session.execute(upsert_meta, batch)

            # Insert Association Records in batches
            if file_server_records:
                unique_fs = list({(r["file_id"], r["server_id"]): r for r in file_server_records}.values())
                stmt_fs = pg_insert(file_servers_association).on_conflict_do_nothing()
                for batch in chunk_list(unique_fs, 1000):
                    await session.execute(stmt_fs, batch)

            if file_vuln_records:
                unique_fv = list({(r["file_id"], r["vulnerability_id"]): r for r in file_vuln_records}.values())
                stmt_fv = pg_insert(file_vulnerabilities_association).on_conflict_do_nothing()
                for batch in chunk_list(unique_fv, 1000):
                    await session.execute(stmt_fv, batch)

            await session.commit()
            logger.info("Successfully committed all dataframes and associations in batches to the database.")
        return StatusResponse(status=status.HTTP_200_OK)

    except Exception as e:
        await handle_db_error(e, "loading dataframes to database", db)
        
        
from contextlib import asynccontextmanager
from collections import Counter
import logging
from pathlib import Path
import sys
from typing import Optional, Union

from fastapi import HTTPException, status, Depends
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.db_connection import AsyncSessionLocal, get_db
from models.api_schemas import (
    FileMetadataFilter,
    FileMetadataListResponse,
    FileMetadataResponse,
    FileMetadataMultiFilter,
    ServerFilter,
    ServerListResponse,
    ServerResponse,
    ServerMultiFilter,
    VulnerabilityFilter,
    VulnerabilityListResponse,
    VulnerabilityResponse,
    VulnerabilityMultiFilter,
    AggregationResponse,
    FileMetadataField, 
    ServerField, 
    VulnerabilityField, 
    AggregationData
)
from models.db_schemas import FileMetadata, Server, Vulnerability
from models.models import (
    FileMetadataModel,
    ServerModel,
    VulnerabilityModel,
    file_servers_association,
    file_vulnerabilities_association,
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# Centralized Error Handling & Session Scope Helper
# -------------------------------------------------------------------------

def handle_db_error(e: Exception, operation: str) -> None:
    """
    Centralized error handler for db_service operations.
    Preserves HTTPExceptions with appropriate logging, logs unexpected or
    SQLAlchemy errors with full traceback, and raises proper HTTPExceptions.
    """
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
        yield db
    else:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


def _normalize_id_list(id_list: Union[list[str], str]) -> list[str]:
    """
    Normalizes input that can be either a list of IDs or a comma-separated string,
    stripping whitespace and removing empty items.
    """
    if isinstance(id_list, str):
        return [item.strip() for item in id_list.split(",") if item.strip()]
    return [str(item).strip() for item in id_list if str(item).strip()]


# -------------------------------------------------------------------------
# Single Entity Retrieval
# -------------------------------------------------------------------------

async def get_server_by_id(_id: str, db: Optional[AsyncSession] = None) -> ServerResponse:
    logger.info(f"Fetching server by _id: '{_id}'")
    if not _id or not _id.strip():
        logger.warning("get_server_by_id called with empty or whitespace-only ID")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server ID cannot be empty.",
        )

    clean_id = _id.strip()

    try:
        async with session_scope(db) as session:
            stmt = select(ServerModel).where(ServerModel._id == clean_id)
            result = await session.execute(stmt)
            server = result.scalars().first()

            if not server:
                logger.warning(f"Server with _id '{clean_id}' was not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Server with id '{clean_id}' not found.",
                )

            logger.info(f"Successfully retrieved server with _id: '{clean_id}'")
            
            return ServerResponse(
                status=status.HTTP_200_OK,
                data=Server.model_validate(server),
            )
    except Exception as e:
        handle_db_error(e, f"fetching server with id '{clean_id}'")


async def get_vulnerability_by_id(_id: str, db: Optional[AsyncSession] = None) -> VulnerabilityResponse:
    logger.info(f"Fetching vulnerability by _id: '{_id}'")
    if not _id or not _id.strip():
        logger.warning("get_vulnerability_by_id called with empty or whitespace-only ID")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vulnerability ID cannot be empty.",
        )

    clean_id = _id.strip()

    try:
        async with session_scope(db) as session:
            stmt = select(VulnerabilityModel).where(VulnerabilityModel._id == clean_id)
            result = await session.execute(stmt)
            vuln = result.scalars().first()

            if not vuln:
                logger.warning(f"Vulnerability with _id '{clean_id}' was not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vulnerability with id '{clean_id}' not found.",
                )

            logger.info(f"Successfully retrieved vulnerability with _id: '{clean_id}'")
            return VulnerabilityResponse(
                status=status.HTTP_200_OK,
                data=Vulnerability.model_validate(vuln),
            )
    except Exception as e:
        handle_db_error(e, f"fetching vulnerability with id '{clean_id}'")


async def get_file_metadata_by_id(_id: str, db: Optional[AsyncSession] = None) -> FileMetadataResponse:
    logger.info(f"Fetching file metadata by _id: '{_id}'")
    if not _id or not _id.strip():
        logger.warning("get_file_metadata_by_id called with empty or whitespace-only ID")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File metadata ID cannot be empty.",
        )

    clean_id = _id.strip()

    try:
        async with session_scope(db) as session:
            stmt = (
                select(FileMetadataModel)
                .options(
                    selectinload(FileMetadataModel.updated_vulnerabilities),
                    selectinload(FileMetadataModel.updated_servers),
                )
                .where(FileMetadataModel._id == clean_id)
            )
            result = await session.execute(stmt)
            file_meta = result.scalars().first()

            if not file_meta:
                logger.warning(f"File metadata with _id '{clean_id}' was not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File metadata with id '{clean_id}' not found.",
                )

            logger.info(f"Successfully retrieved file metadata with _id: '{clean_id}'")
            return FileMetadataResponse(
                status=status.HTTP_200_OK,
                data=FileMetadata.model_validate(file_meta),
            )
    except Exception as e:
        handle_db_error(e, f"fetching file metadata with id '{clean_id}'")


# -------------------------------------------------------------------------
# Multiple Entity Retrieval by ID List
# -------------------------------------------------------------------------

async def get_servers_by_id_list(
    id_list: Union[list[str], str], db: Optional[AsyncSession] = None
) -> ServerListResponse:
    cleaned_ids = _normalize_id_list(id_list)
    logger.info(f"Fetching servers for {len(cleaned_ids)} ID(s)")
    if not cleaned_ids:
        logger.warning("get_servers_by_id_list called with empty ID list")
        return ServerListResponse(status=status.HTTP_200_OK, data=[])

    try:
        async with session_scope(db) as session:
            stmt = select(ServerModel).where(ServerModel._id.in_(cleaned_ids))
            result = await session.execute(stmt)
            servers = result.scalars().all()

            logger.info(
                f"Retrieved {len(servers)} server record(s) out of {len(cleaned_ids)} requested ID(s)"
            )
            return ServerListResponse(
                status=status.HTTP_200_OK,
                data=[Server.model_validate(s) for s in servers],
            )
    except Exception as e:
        handle_db_error(e, f"fetching servers by id list ({len(cleaned_ids)} IDs)")


async def get_vulnerabilities_by_id_list(
    id_list: Union[list[str], str], db: Optional[AsyncSession] = None
) -> VulnerabilityListResponse:
    cleaned_ids = _normalize_id_list(id_list)
    logger.info(f"Fetching vulnerabilities for {len(cleaned_ids)} ID(s)")
    if not cleaned_ids:
        logger.warning("get_vulnerabilities_by_id_list called with empty ID list")
        return VulnerabilityListResponse(status=status.HTTP_200_OK, data=[])

    try:
        async with session_scope(db) as session:
            stmt = select(VulnerabilityModel).where(VulnerabilityModel._id.in_(cleaned_ids))
            result = await session.execute(stmt)
            vulns = result.scalars().all()

            logger.info(
                f"Retrieved {len(vulns)} vulnerability record(s) out of {len(cleaned_ids)} requested ID(s)"
            )
            return VulnerabilityListResponse(
                status=status.HTTP_200_OK,
                data=[Vulnerability.model_validate(v) for v in vulns],
            )
    except Exception as e:
        handle_db_error(e, f"fetching vulnerabilities by id list ({len(cleaned_ids)} IDs)")


async def get_files_metadata_by_id_list(
    id_list: Union[list[str], str], db: Optional[AsyncSession] = None
) -> FileMetadataListResponse:
    cleaned_ids = _normalize_id_list(id_list)
    logger.info(f"Fetching files metadata for {len(cleaned_ids)} ID(s)")
    if not cleaned_ids:
        logger.warning("get_files_metadata_by_id_list called with empty ID list")
        return FileMetadataListResponse(status=status.HTTP_200_OK, data=[])

    try:
        async with session_scope(db) as session:
            stmt = (
                select(FileMetadataModel)
                .options(
                    selectinload(FileMetadataModel.updated_vulnerabilities),
                    selectinload(FileMetadataModel.updated_servers),
                )
                .where(FileMetadataModel._id.in_(cleaned_ids))
            )
            result = await session.execute(stmt)
            files = result.scalars().all()

            logger.info(
                f"Retrieved {len(files)} file metadata record(s) out of {len(cleaned_ids)} requested ID(s)"
            )
            return FileMetadataListResponse(
                status=status.HTTP_200_OK,
                data=[FileMetadata.model_validate(f) for f in files],
            )
    except Exception as e:
        handle_db_error(e, f"fetching files metadata by id list ({len(cleaned_ids)} IDs)")


# -------------------------------------------------------------------------
# Relational Queries & Cross-Entity Search
# -------------------------------------------------------------------------

async def get_servers_with_vulnerability(
    _id: str, db: Optional[AsyncSession] = None
) -> ServerListResponse:
    logger.info(f"Fetching servers with vulnerability identifier: '{_id}'")
    if not _id or not _id.strip():
        logger.warning("get_servers_with_vulnerability called with empty or whitespace-only ID")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vulnerability identifier cannot be empty.",
        )

    clean_id = _id.strip()
    try:
        async with session_scope(db) as session:
            stmt = (
                select(ServerModel)
                .join(VulnerabilityModel, ServerModel._id == VulnerabilityModel.server_id)
                .where(
                    or_(
                        VulnerabilityModel._id == clean_id,
                        VulnerabilityModel.vulnerability_type_id == clean_id,
                    )
                )
                .distinct()
            )
            result = await session.execute(stmt)
            servers = result.scalars().all()

            logger.info(
                f"Found {len(servers)} distinct server(s) affected by vulnerability identifier '{clean_id}'"
            )
            return ServerListResponse(
                status=status.HTTP_200_OK,
                data=[Server.model_validate(s) for s in servers],
            )
    except Exception as e:
        handle_db_error(e, f"fetching servers with vulnerability '{clean_id}'")


async def get_servers_with_vulnerabilities(
    id_list: Union[list[str], str], db: Optional[AsyncSession] = None
) -> ServerListResponse:
    cleaned_ids = _normalize_id_list(id_list)
    logger.info(f"Fetching servers affected by any of {len(cleaned_ids)} vulnerability ID(s)")
    if not cleaned_ids:
        logger.warning("get_servers_with_vulnerabilities called with empty ID list")
        return ServerListResponse(status=status.HTTP_200_OK, data=[])

    try:
        async with session_scope(db) as session:
            stmt = (
                select(ServerModel)
                .join(VulnerabilityModel, ServerModel._id == VulnerabilityModel.server_id)
                .where(
                    or_(
                        VulnerabilityModel._id.in_(cleaned_ids),
                        VulnerabilityModel.vulnerability_type_id.in_(cleaned_ids),
                    )
                )
                .distinct()
            )
            result = await session.execute(stmt)
            servers = result.scalars().all()

            logger.info(
                f"Found {len(servers)} distinct server(s) affected by {len(cleaned_ids)} vulnerability identifier(s)"
            )
            return ServerListResponse(
                status=status.HTTP_200_OK,
                data=[Server.model_validate(s) for s in servers],
            )
    except Exception as e:
        handle_db_error(e, f"fetching servers with vulnerabilities list ({len(cleaned_ids)} IDs)")


async def get_files_that_update_server(
    _id: str, db: Optional[AsyncSession] = None
) -> FileMetadataListResponse:
    logger.info(f"Fetching files that updated server _id: '{_id}'")
    if not _id or not _id.strip():
        logger.warning("get_files_that_update_server called with empty or whitespace-only ID")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server ID cannot be empty.",
        )

    clean_id = _id.strip()
    try:
        async with session_scope(db) as session:
            stmt = (
                select(FileMetadataModel)
                .join(
                    file_servers_association,
                    FileMetadataModel._id == file_servers_association.c.file_id,
                )
                .where(file_servers_association.c.server_id == clean_id)
                .options(
                    selectinload(FileMetadataModel.updated_vulnerabilities),
                    selectinload(FileMetadataModel.updated_servers),
                )
                .distinct()
            )
            result = await session.execute(stmt)
            files = result.scalars().all()

            logger.info(
                f"Found {len(files)} file metadata record(s) that updated server '{clean_id}'"
            )
            return FileMetadataListResponse(
                status=status.HTTP_200_OK,
                data=[FileMetadata.model_validate(f) for f in files],
            )
    except Exception as e:
        handle_db_error(e, f"fetching files that updated server '{clean_id}'")


# -------------------------------------------------------------------------
# First N Entity Retrieval
# -------------------------------------------------------------------------

async def fetch_first_n_vulnerabilities(
    limit: int, db: Optional[AsyncSession] = None
) -> VulnerabilityListResponse:
    logger.info(f"Fetching first {limit} vulnerabilities")
    if limit <= 0:
        logger.warning(f"fetch_first_n_vulnerabilities called with non-positive limit: {limit}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be a positive integer greater than 0.",
        )

    try:
        async with session_scope(db) as session:
            stmt = select(VulnerabilityModel).limit(limit)
            result = await session.execute(stmt)
            vulns = result.scalars().all()

            logger.info(f"Successfully fetched {len(vulns)} vulnerabilities (requested limit: {limit})")
            return VulnerabilityListResponse(
                status=status.HTTP_200_OK,
                data=[Vulnerability.model_validate(v) for v in vulns],
            )
    except Exception as e:
        handle_db_error(e, f"fetching first {limit} vulnerabilities")


async def fetch_first_n_servers(
    limit: int, db: Optional[AsyncSession] = None
) -> ServerListResponse:
    logger.info(f"Fetching first {limit} servers")
    if limit <= 0:
        logger.warning(f"fetch_first_n_servers called with non-positive limit: {limit}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be a positive integer greater than 0.",
        )

    try:
        async with session_scope(db) as session:
            stmt = select(ServerModel).limit(limit)
            result = await session.execute(stmt)
            servers = result.scalars().all()

            logger.info(f"Successfully fetched {len(servers)} servers (requested limit: {limit})")
            return ServerListResponse(
                status=status.HTTP_200_OK,
                data=[Server.model_validate(s) for s in servers],
            )
    except Exception as e:
        handle_db_error(e, f"fetching first {limit} servers")


async def fetch_first_n_metadata_files(
    limit: int, db: Optional[AsyncSession] = None
) -> FileMetadataListResponse:
    logger.info(f"Fetching first {limit} metadata files")
    if limit <= 0:
        logger.warning(f"fetch_first_n_metadata_files called with non-positive limit: {limit}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be a positive integer greater than 0.",
        )

    try:
        async with session_scope(db) as session:
            stmt = (
                select(FileMetadataModel)
                .options(
                    selectinload(FileMetadataModel.updated_vulnerabilities),
                    selectinload(FileMetadataModel.updated_servers),
                )
                .limit(limit)
            )
            result = await session.execute(stmt)
            files = result.scalars().all()

            logger.info(f"Successfully fetched {len(files)} metadata files (requested limit: {limit})")
            return FileMetadataListResponse(
                status=status.HTTP_200_OK,
                data=[FileMetadata.model_validate(f) for f in files],
            )
    except Exception as e:
        handle_db_error(e, f"fetching first {limit} metadata files")


# -------------------------------------------------------------------------
# Filtered Queries
# -------------------------------------------------------------------------

async def get_vulnerability_filtered(
    filters: VulnerabilityFilter, db: Optional[AsyncSession] = Depends(get_db)
) -> VulnerabilityListResponse:
    """
    Returns all VulnerabilityModel rows that match every non-None field in
    *filters* (AND semantics).  An empty/all-None filter returns all rows.
    """
    logger.info(f"Fetching vulnerabilities with filters: {filters.model_dump(exclude_none=True)}")
    try:
        async with session_scope(db) as session:
            stmt = select(VulnerabilityModel)
            for field, value in filters.model_dump(exclude_none=True).items():
                column = getattr(VulnerabilityModel, field)
                stmt = stmt.where(column == value)
            result = await session.execute(stmt)
            vulns = result.scalars().all()
            logger.info(f"Filtered vulnerability query returned {len(vulns)} record(s)")
            return VulnerabilityListResponse(
                status=200,
                data=[Vulnerability.model_validate(v) for v in vulns],
            )
    except Exception as e:
        handle_db_error(e, "fetching filtered vulnerabilities")


async def get_server_filtered(
    filters: ServerFilter, db: Optional[AsyncSession] = Depends(get_db)
) -> ServerListResponse:
    """
    Returns all ServerModel rows that match every non-None field in
    *filters* (AND semantics).  An empty/all-None filter returns all rows.
    """
    logger.info(f"Fetching servers with filters: {filters.model_dump(exclude_none=True)}")
    try:
        async with session_scope(db) as session:
            stmt = select(ServerModel)
            for field, value in filters.model_dump(exclude_none=True).items():
                column = getattr(ServerModel, field)
                stmt = stmt.where(column == value)
            result = await session.execute(stmt)
            servers = result.scalars().all()
            logger.info(f"Filtered server query returned {len(servers)} record(s)")
            return ServerListResponse(
                status=200,
                data=[Server.model_validate(s) for s in servers],
            )
    except Exception as e:
        handle_db_error(e, "fetching filtered servers")


async def get_file_metadata_filtered(
    filters: FileMetadataFilter, db: Optional[AsyncSession] = Depends(get_db)
) -> FileMetadataListResponse:
    """
    Returns all FileMetadataModel rows that match every non-None field in
    *filters* (AND semantics).  An empty/all-None filter returns all rows.
    """
    logger.info(f"Fetching file metadata with filters: {filters.model_dump(exclude_none=True)}")
    try:
        async with session_scope(db) as session:
            stmt = (
                select(FileMetadataModel)
                .options(
                    selectinload(FileMetadataModel.updated_vulnerabilities),
                    selectinload(FileMetadataModel.updated_servers),
                )
            )
            for field, value in filters.model_dump(exclude_none=True).items():
                column = getattr(FileMetadataModel, field)
                stmt = stmt.where(column == value)
            result = await session.execute(stmt)
            files = result.scalars().all()
            logger.info(f"Filtered file metadata query returned {len(files)} record(s)")
            return FileMetadataListResponse(
                status=200,
                data=[FileMetadata.model_validate(f) for f in files],
            )
    except Exception as e:
        handle_db_error(e, "fetching filtered file metadata")


# -------------------------------------------------------------------------
# Multi-value Filtered Queries  (IN semantics)
# -------------------------------------------------------------------------

async def get_vulnerability_multi_filtered(
    filters: VulnerabilityMultiFilter, db: Optional[AsyncSession] = Depends(get_db)
) -> VulnerabilityListResponse:
    """
    Returns VulnerabilityModel rows where each provided field matches ANY value
    in its list (column IN list).  Conditions across different fields are
    combined with AND.  Empty/all-None filter returns all rows.
    """
    active = {f: v for f, v in filters.model_dump(exclude_none=True).items() if v}
    logger.info(f"Fetching vulnerabilities with multi-value filters: {active}")
    try:
        async with session_scope(db) as session:
            stmt = select(VulnerabilityModel)
            for field, values in active.items():
                column = getattr(VulnerabilityModel, field)
                stmt = stmt.where(column.in_(values))
            result = await session.execute(stmt)
            vulns = result.scalars().all()
            logger.info(f"Multi-filter vulnerability query returned {len(vulns)} record(s)")
            return VulnerabilityListResponse(
                status=200,
                data=[Vulnerability.model_validate(v) for v in vulns],
            )
    except Exception as e:
        handle_db_error(e, "fetching multi-filtered vulnerabilities")


async def get_server_multi_filtered(
    filters: ServerMultiFilter, db: Optional[AsyncSession] = Depends(get_db)
) -> ServerListResponse:
    """
    Returns ServerModel rows where each provided field matches ANY value in its
    list (column IN list).  Conditions across different fields are combined with
    AND.  Empty/all-None filter returns all rows.
    """
    active = {f: v for f, v in filters.model_dump(exclude_none=True).items() if v}
    logger.info(f"Fetching servers with multi-value filters: {active}")
    try:
        async with session_scope(db) as session:
            stmt = select(ServerModel)
            for field, values in active.items():
                column = getattr(ServerModel, field)
                stmt = stmt.where(column.in_(values))
            result = await session.execute(stmt)
            servers = result.scalars().all()
            logger.info(f"Multi-filter server query returned {len(servers)} record(s)")
            return ServerListResponse(
                status=200,
                data=[Server.model_validate(s) for s in servers],
            )
    except Exception as e:
        handle_db_error(e, "fetching multi-filtered servers")


async def get_file_metadata_multi_filtered(
    filters: FileMetadataMultiFilter, db: Optional[AsyncSession] = Depends(get_db)
) -> FileMetadataListResponse:
    """
    Returns FileMetadataModel rows where each provided field matches ANY value
    in its list (column IN list).  Conditions across different fields are
    combined with AND.  Empty/all-None filter returns all rows.
    """
    active = {f: v for f, v in filters.model_dump(exclude_none=True).items() if v}
    logger.info(f"Fetching file metadata with multi-value filters: {active}")
    try:
        async with session_scope(db) as session:
            stmt = (
                select(FileMetadataModel)
                .options(
                    selectinload(FileMetadataModel.updated_vulnerabilities),
                    selectinload(FileMetadataModel.updated_servers),
                )
            )
            for field, values in active.items():
                column = getattr(FileMetadataModel, field)
                stmt = stmt.where(column.in_(values))
            result = await session.execute(stmt)
            files = result.scalars().all()
            logger.info(f"Multi-filter file metadata query returned {len(files)} record(s)")
            return FileMetadataListResponse(
                status=200,
                data=[FileMetadata.model_validate(f) for f in files],
            )
    except Exception as e:
        handle_db_error(e, "fetching multi-filtered file metadata")


def vuln_aggregate_by(vuln_payload: VulnerabilityListResponse, column: VulnerabilityField) -> AggregationData:
    vulns = vuln_payload.data
    aggregated_vulns = Counter(getattr(vuln, column) for vuln in vulns)
    
    return AggregationResponse(
        status=200,
        data=aggregated_vulns
    )
    

def server_aggregate_by(server_payload: ServerListResponse, column: ServerField) -> AggregationData:
    servers = server_payload.data
    aggregated_servers = Counter(getattr(server, column) for server in servers)
    
    return AggregationResponse(
        status=200,
        data=aggregated_servers
    )

def filemetadata_aggregate_by(filemetadata_payload: FileMetadataListResponse, column: FileMetadataField) -> AggregationData:
    filemetadatas = filemetadata_payload.data
    aggregated_filemetadata = Counter(getattr(filemetadata, column) for filemetadata in filemetadatas)
    
    return AggregationResponse(
        status=200,
        data=aggregated_filemetadata
    )
    
# Define Microservices for Dependency Injection
def multi_vuln_aggregate_by(column: VulnerabilityField, vuln_payload = Depends(get_vulnerability_multi_filtered)):
    return vuln_aggregate_by(vuln_payload, column)

def single_vuln_aggregate_by(column: VulnerabilityField, vuln_payload = Depends(get_vulnerability_filtered)):
    return vuln_aggregate_by(vuln_payload, column)

def multi_server_aggregate_by(column: ServerField, server_payload = Depends(get_server_multi_filtered)):
    return server_aggregate_by(server_payload, column)

def single_server_aggregate_by(column: ServerField, server_payload = Depends(get_server_filtered)):
    return server_aggregate_by(server_payload, column)

def multi_filemetadata_aggregate_by(column: FileMetadataField, filemetadata_payload = Depends(get_file_metadata_multi_filtered)):
    return filemetadata_aggregate_by(filemetadata_payload, column)

def single_filemetadata_aggregate_by(column: FileMetadataField, filemetadata_payload = Depends(get_file_metadata_filtered)):
    return filemetadata_aggregate_by(filemetadata_payload, column)

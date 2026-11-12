from pathlib import Path
import sys

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.db_connection import get_db
from models.api_schemas import (
    FileMetadataFilter,
    FileMetadataListResponse,
    FileMetadataResponse,
    FileMetadataMultiFilter,
    IdListRequest,
    ServerFilter,
    ServerListResponse,
    ServerResponse,
    ServerMultiFilter,
    VulnerabilityFilter,
    VulnerabilityListResponse,
    VulnerabilityResponse,
    VulnerabilityMultiFilter,
    AggregationResponse
)
import services.db_service_retrival as db_service_retrival

router = APIRouter(prefix="/db", tags=["DatabaseRetrival"])


# -------------------------------------------------------------------------
# First N Entity Endpoints
# -------------------------------------------------------------------------

@router.get("/vulnerabilities/first/{limit}", response_model=VulnerabilityListResponse)
async def fetch_first_vulnerabilities(
    limit: int, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.fetch_first_n_vulnerabilities(limit=limit, db=db)


@router.get("/servers/first/{limit}", response_model=ServerListResponse)
async def fetch_first_servers(
    limit: int, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.fetch_first_n_servers(limit=limit, db=db)


@router.get("/files/first/{limit}", response_model=FileMetadataListResponse)
async def fetch_first_files(
    limit: int, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.fetch_first_n_metadata_files(limit=limit, db=db)


# -------------------------------------------------------------------------
# Batch Retrieval by ID List Endpoints
# -------------------------------------------------------------------------

@router.post("/servers/by-ids", response_model=ServerListResponse)
async def get_servers_by_ids(
    request: IdListRequest, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.get_servers_by_id_list(id_list=request.id_list, db=db)


@router.post("/vulnerabilities/by-ids", response_model=VulnerabilityListResponse)
async def get_vulnerabilities_by_ids(
    request: IdListRequest, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.get_vulnerabilities_by_id_list(id_list=request.id_list, db=db)


@router.post("/files/by-ids", response_model=FileMetadataListResponse)
async def get_files_by_ids(
    request: IdListRequest, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.get_files_metadata_by_id_list(id_list=request.id_list, db=db)


# -------------------------------------------------------------------------
# Cross-Entity / Relational Search Endpoints
# -------------------------------------------------------------------------

@router.get("/servers/with-vulnerability/{_id}", response_model=ServerListResponse)
async def get_servers_with_vulnerability(
    _id: str, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.get_servers_with_vulnerability(_id=_id, db=db)


@router.post("/servers/with-vulnerabilities", response_model=ServerListResponse)
async def get_servers_with_vulnerabilities(
    request: IdListRequest, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.get_servers_with_vulnerabilities(id_list=request.id_list, db=db)


@router.get("/files/updates-for-server/{_id}", response_model=FileMetadataListResponse)
async def get_files_that_update_server(
    _id: str, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.get_files_that_update_server(_id=_id, db=db)


# -------------------------------------------------------------------------
# Single Entity by ID Endpoints
# -------------------------------------------------------------------------

@router.get("/servers/{_id}", response_model=ServerResponse)
async def get_server(
    _id: str, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.get_server_by_id(_id=_id, db=db)


@router.get("/vulnerabilities/{_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(
    _id: str, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.get_vulnerability_by_id(_id=_id, db=db)


@router.get("/files/{_id}", response_model=FileMetadataResponse)
async def get_file_metadata(
    _id: str, db: AsyncSession = Depends(get_db)
):
    return await db_service_retrival.get_file_metadata_by_id(_id=_id, db=db)


# -------------------------------------------------------------------------
# Filtered Query Endpoints
# -------------------------------------------------------------------------

@router.post("/vulnerabilities/filtered", response_model=VulnerabilityListResponse)
async def get_vulnerabilities_filtered(
    filters: VulnerabilityFilter,
    db: AsyncSession = Depends(get_db),
):
    return await db_service_retrival.get_vulnerability_filtered(filters=filters, db=db)


@router.post("/servers/filtered", response_model=ServerListResponse)
async def get_servers_filtered(
    filters: ServerFilter,
    db: AsyncSession = Depends(get_db),
):
    return await db_service_retrival.get_server_filtered(filters=filters, db=db)


@router.post("/files/filtered", response_model=FileMetadataListResponse)
async def get_files_metadata_filtered(
    filters: FileMetadataFilter,
    db: AsyncSession = Depends(get_db),
):
    return await db_service_retrival.get_file_metadata_filtered(filters=filters, db=db)


# -------------------------------------------------------------------------
# Multi-value Filtered Query Endpoints  (IN semantics)
# -------------------------------------------------------------------------

@router.post("/vulnerabilities/filtered/multi", response_model=VulnerabilityListResponse)
async def get_vulnerabilities_multi_filtered(
    filters: VulnerabilityMultiFilter,
    db: AsyncSession = Depends(get_db),
):
    return await db_service_retrival.get_vulnerability_multi_filtered(filters=filters, db=db)


@router.post("/servers/filtered/multi", response_model=ServerListResponse)
async def get_servers_multi_filtered(
    filters: ServerMultiFilter,
    db: AsyncSession = Depends(get_db),
):
    return await db_service_retrival.get_server_multi_filtered(filters=filters, db=db)


@router.post("/files/filtered/multi", response_model=FileMetadataListResponse)
async def get_files_metadata_multi_filtered(
    filters: FileMetadataMultiFilter,
    db: AsyncSession = Depends(get_db),
):
    return await db_service_retrival.get_file_metadata_multi_filtered(filters=filters, db=db)

@router.post("/vulnerabilities/filtered/multi/agg", response_model=AggregationResponse)
async def get_vulns_multi_filtered_aggregated(
    response: AggregationResponse = Depends(db_service_retrival.multi_vuln_aggregate_by)
):
    return response

@router.post("/servers/filtered/multi/agg", response_model=AggregationResponse)
async def get_servers_multi_filtered_aggregated(
    response: AggregationResponse = Depends(db_service_retrival.multi_server_aggregate_by)
):
    return response

@router.post("/files/filtered/multi/agg", response_model=AggregationResponse)
async def get_files_metadata_multi_filtered_aggregated(
    response: AggregationResponse = Depends(db_service_retrival.multi_filemetadata_aggregate_by)
):
    return response


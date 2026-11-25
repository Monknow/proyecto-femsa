from pathlib import Path
import sys
from typing import Tuple, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

import logging

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.db_connection import get_db
from models.api_schemas import (
    FileMetadataListResponse,
    FileMetadataResponse,
    IdListRequest,
    ServerListResponse,
    ServerResponse,
    VulnerabilityListResponse,
    VulnerabilityResponse,
    StatusResponse
)

from models.models import FileMetadataModel
from services.raw_file_storage import delete_raw_file, find_raw_file, save_raw_file

import services.db_service_population as db_service_population

from models.df_schemas import ServerDataFrameSchema, VulnerabilityDataFrameSchema, FileMetadataDataFrameSchema
from utils.file_uploads import process_excel_upload

router = APIRouter(prefix="/db", tags=["DatabasePopulation"])
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# Populate DataBase
# -------------------------------------------------------------------------

@router.post("/load", response_model=StatusResponse)
async def load_file_from_excel(
    file: UploadFile = File(...),
    df_tuple: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] = Depends(process_excel_upload),
    db: AsyncSession = Depends(get_db)
):
    result = await db_service_population.load_dataframes_to_db(df_tuple[0], df_tuple[1], df_tuple[2], db)

    # Keep the raw upload (named after its file id) so it can be downloaded later.
    file_id = str(df_tuple[2]["_id"].iloc[0])
    try:
        await file.seek(0)
        await save_raw_file(file_id, await file.read(), file.filename)
    except Exception as exc:
        logger.error(f"Could not store raw file '{file.filename}' ({file_id}): {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The data was loaded but the raw file could not be stored.",
        )
    return result


@router.get("/files/{_id}/download")
async def download_raw_file(_id: str, db: AsyncSession = Depends(get_db)):
    path = find_raw_file(_id)
    if path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Raw file not found.")
    meta = await db.get(FileMetadataModel, _id)
    filename = meta.file_name if meta else path.name
    return FileResponse(path, filename=filename)


@router.delete("/files/{_id}", response_model=StatusResponse)
async def delete_file(_id: str, db: AsyncSession = Depends(get_db)):
    """Deletes the file's metadata, the data only it contributed, and its raw copy."""
    result = await db_service_population.delete_file_data(_id, db)
    delete_raw_file(_id)
    return result

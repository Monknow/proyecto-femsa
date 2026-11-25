from pathlib import Path
import sys
from typing import Tuple, List

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
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

from services.excel_archive import archive_uploaded_excel

import services.db_service_population as db_service_population

from models.df_schemas import ServerDataFrameSchema, VulnerabilityDataFrameSchema, FileMetadataDataFrameSchema
from utils.file_uploads import process_excel_upload

router = APIRouter(prefix="/db", tags=["DatabasePopulation"])
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# Populate DataBase
# -------------------------------------------------------------------------

async def archive_excel_on_upload(file: UploadFile = File(...), save_excel: bool = Form(False)):
    """
    Archives a timestamped copy of the uploaded Excel into `uploaded_excels/`
    after /load finishes saving to the database.
    """
    yield  

    if not save_excel:
        return

    try:
        await file.seek(0)
        file_bytes = await file.read()
        archived_path = await archive_uploaded_excel(
            file_bytes=file_bytes,
            original_filename=file.filename or "upload.xlsx",
        )
        logger.info(f"Archived uploaded Excel to: {archived_path}")
    except Exception as exc:
        # Log any disk issue without breaking the user's database upload response
        logger.error(f"Could not archive Excel '{file.filename}': {exc}")
        

@router.post("/load", response_model=StatusResponse, dependencies=[Depends(archive_excel_on_upload)],)
async def load_file_from_excel(
    df_tuple: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] = Depends(process_excel_upload), 
    
    db: AsyncSession = Depends(get_db)
):
    return await db_service_population.load_dataframes_to_db(df_tuple[0], df_tuple[1], df_tuple[2], db)

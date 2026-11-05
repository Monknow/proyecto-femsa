from pathlib import Path
import sys
from typing import Tuple, List

from fastapi import APIRouter, Depends, status
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

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

import services.db_service_population as db_service_population

from models.df_schemas import ServerDataFrameSchema, VulnerabilityDataFrameSchema, FileMetadataDataFrameSchema
from utils.file_uploads import process_excel_upload

router = APIRouter(prefix="/db", tags=["DatabasePopulation"])


# -------------------------------------------------------------------------
# Populate DataBase
# -------------------------------------------------------------------------

@router.post("/load", response_model=StatusResponse)
async def load_file_from_excel(
    df_tuple: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] = Depends(process_excel_upload), 
    
    db: AsyncSession = Depends(get_db)
):
    return await db_service_population.load_dataframes_to_db(df_tuple[0], df_tuple[1], df_tuple[2], db)

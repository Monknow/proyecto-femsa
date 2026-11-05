import sys
import logging
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings
from fastapi.middleware.cors import CORSMiddleware
from core.db_connection import get_db, engine, Base
from config import settings
import models.models
import routes.db_retrival as db_routes_retrival
import routes.db_population as db_routes_population

logger = logging.getLogger(__name__)


# Lifecycle of Backend
@asynccontextmanager
async def lifespan(app: FastAPI):
    # begin of lifecicle
    logger.info('Starting server...')
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    
    logger.info("Shutting down backend...")


app = FastAPI(
    title='Backend for Femsa Server Vulnerabilities Management',
    description='A FastAPI Backend for managing server vulnerability data from Femsa',
    version='1.0.0',
    lifespan=lifespan,
    docs_url = '/docs' if settings.environment == 'development' else None,
    redoc_url = '/redoc' if settings.environment == 'development' else None,
    openapi_url = '/openapi.json' if settings.environment == 'development' else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False, # no session cookies
    allow_methods=["POST", "DELETE", "GET", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(db_routes_retrival.router)
app.include_router(db_routes_population.router)

@app.get("/healthz", tags=["System"])
def health_check(db: AsyncSession = Depends(get_db)):
    return {
      "status": "success",
      "message": "App and PostgreSQL connection up and running!",
    }


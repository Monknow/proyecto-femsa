import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    allowed_origins: list[str] = [""]
    environment: str = ""

    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # lifecycle
    yield
    
    # end of lifecicle
    logger.info("Shutting backend...")

@app.get("/healthz", tags=["System"])
def health_check():
    return {"status": "ok"}

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import logging
import sys
from config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.postgre_uri, echo=True)

AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()


async def get_db():
  async with AsyncSessionLocal() as session:
    try:
      yield session
    
    except Exception as e:
      logger.critical('DB INIT FAILURE. SHUTTING DOWN...')
      sys.exit(1)
    finally:
      await session.close()
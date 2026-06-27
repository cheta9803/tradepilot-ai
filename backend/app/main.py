from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TradePilot AI started")
    yield
    logger.info("TradePilot AI stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(api_router)
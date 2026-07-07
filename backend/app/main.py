from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import logger
from app.instruments.cache import InstrumentCache
from app.live.instance import live_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    InstrumentCache.load()

    live_manager.start()

    logger.info("TradePilot AI started")

    yield

    live_manager.stop()

    logger.info("TradePilot AI stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(api_router)
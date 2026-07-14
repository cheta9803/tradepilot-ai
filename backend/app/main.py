from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.candles.history_loader import CandleHistoryLoader
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import logger
from app.db.session import SessionLocal
from app.instruments.cache import InstrumentCache
from app.live.instance import live_manager
from app.history.rebuilder import HistoryRebuilder


@asynccontextmanager
async def lifespan(app: FastAPI):

    InstrumentCache.load()

    db = SessionLocal()

    try:
        CandleHistoryLoader.load(db)
    finally:
        db.close()

    # Build all higher timeframes from existing 1m history
    HistoryRebuilder.rebuild()

    # Start live websocket
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
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.angel.client import AngelClient
from app.api.router import api_router
from app.candles.history_loader import CandleHistoryLoader
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import logger
from app.db.session import SessionLocal
from app.execution.instance import execution_manager
from app.history.rebuilder import HistoryRebuilder
from app.instruments.cache import InstrumentCache
from app.live.instance import live_manager

from app.startup.recovery import StartupRecovery

from fastapi.middleware.cors import CORSMiddleware

from app.websocket.router import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    InstrumentCache.load()

    db = SessionLocal()

    try:
        CandleHistoryLoader.load(db)
    finally:
        db.close()

    HistoryRebuilder.rebuild()

    AngelClient.login()

    StartupRecovery.recover()

    execution_manager.start()

    live_manager.start()

    logger.info("TradePilot AI started")

    yield

    execution_manager.stop()

    live_manager.stop()

    logger.info("TradePilot AI stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router)

app.include_router(
    websocket_router,
)
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.angel.client import AngelClient
from app.api.router import api_router
from app.candles.history_loader import CandleHistoryLoader
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import logger
from app.db.session import SessionLocal
from app.execution.instance import execution_manager

from app.instruments.cache import InstrumentCache
from app.live.instance import live_manager
from app.startup.recovery import StartupRecovery
from app.websocket.manager import websocket_manager
from app.websocket.router import router as websocket_router
from app.paper_trading.api import router as paper_trading_router


async def _start_live_manager() -> None:
    """
    Start the live manager without blocking FastAPI startup.

    live_manager.start() performs watchlist/history initialization,
    which can involve Angel One historical API calls and rate limiting.
    Running it in a worker thread allows the API to become available
    immediately.
    """
    try:
        await asyncio.to_thread(
            live_manager.start,
        )

        logger.info(
            "Live manager background initialization completed.",
        )

    except Exception as exc:
        logger.warning(
            "Live manager background initialization failed: %s",
            exc,
        )


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    websocket_manager.set_loop(
        asyncio.get_running_loop(),
    )

    try:
        InstrumentCache.load()

    except Exception as exc:
        logger.warning(
            "Instrument cache initialization failed: %s",
            exc,
        )

    db = SessionLocal()

    try:
        try:
            CandleHistoryLoader.load(
                db,
            )

        except Exception as exc:
            logger.warning(
                "Candle history initialization failed: %s",
                exc,
            )

    finally:
        db.close()

    try:
        AngelClient.login()

        logger.info(
            "Angel client initialized successfully.",
        )

    except Exception as exc:
        logger.warning(
            "Angel client initialization failed during startup: %s",
            exc,
        )

    try:
        StartupRecovery.recover()

    except Exception as exc:
        logger.warning(
            "Startup recovery failed: %s",
            exc,
        )

    try:
        execution_manager.start()

    except Exception as exc:
        logger.warning(
            "Execution manager failed to start: %s",
            exc,
        )

    # ---------------------------------------------------------
    # IMPORTANT:
    #
    # live_manager.start() performs potentially heavy history
    # loading for the watchlist/Nifty universe.
    #
    # Do NOT block FastAPI startup on this operation.
    # ---------------------------------------------------------
    live_manager_task = asyncio.create_task(
        _start_live_manager(),
    )

    logger.info(
        "TradePilot AI started. "
        "Live manager initialization is running in background.",
    )

    # FastAPI becomes ready here.
    yield

    # ---------------------------------------------------------
    # Shutdown
    # ---------------------------------------------------------

    try:
        execution_manager.stop()

    except Exception as exc:
        logger.warning(
            "Execution manager shutdown failed: %s",
            exc,
        )

    try:
        live_manager.stop()

    except Exception as exc:
        logger.warning(
            "Live manager shutdown failed: %s",
            exc,
        )

    # The live manager normally finishes its own background
    # initialization. Cancel only the asyncio wrapper if it is
    # still pending during application shutdown.
    if not live_manager_task.done():
        live_manager_task.cancel()

        try:
            await live_manager_task

        except asyncio.CancelledError:
            pass

    logger.info(
        "TradePilot AI stopped",
    )


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

register_exception_handlers(
    app,
)

app.include_router(
    api_router,
)

app.include_router(
    websocket_router,
)

app.include_router(
    paper_trading_router,
)
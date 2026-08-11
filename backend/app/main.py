from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.candles.history_loader import CandleHistoryLoader
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import logger
from app.db.session import SessionLocal
from app.execution.instance import execution_manager
from app.instruments.cache import InstrumentCache
from app.live.instance import live_manager
from app.paper_trading.api import router as paper_trading_router
from app.startup.recovery import StartupRecovery
from app.websocket.manager import websocket_manager
from app.websocket.router import router as websocket_router


async def _start_live_manager() -> None:
    """
    Start the live manager without blocking FastAPI startup.

    LiveManager is responsible for:
        1. Angel One authentication.
        2. Angel WebSocket initialization.
        3. Live market subscriptions.
        4. Background historical warm-up.

    Historical warm-up must not block FastAPI startup.
    """

    try:

        await asyncio.to_thread(
            live_manager.start,
        )

        logger.info(
            "Live manager background initialization completed.",
        )

    except Exception as exc:

        logger.exception(
            "Live manager background initialization failed: %s",
            exc,
        )


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    # ---------------------------------------------------------
    # Register the FastAPI event loop.
    #
    # Angel WebSocket runs on a separate thread and uses this
    # loop to broadcast market ticks to the frontend.
    # ---------------------------------------------------------

    websocket_manager.set_loop(
        asyncio.get_running_loop(),
    )

    # ---------------------------------------------------------
    # Load instrument master/cache.
    # ---------------------------------------------------------

    try:

        InstrumentCache.load()

    except Exception as exc:

        logger.warning(
            "Instrument cache initialization failed: %s",
            exc,
        )

    # ---------------------------------------------------------
    # Load locally persisted candle history.
    #
    # This is DB/cache initialization only.
    # Angel historical API is NOT called here.
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Startup recovery.
    # ---------------------------------------------------------

    try:

        StartupRecovery.recover()

    except Exception as exc:

        logger.warning(
            "Startup recovery failed: %s",
            exc,
        )

    # ---------------------------------------------------------
    # Start execution manager.
    # ---------------------------------------------------------

    try:

        execution_manager.start()

    except Exception as exc:

        logger.warning(
            "Execution manager failed to start: %s",
            exc,
        )

    # ---------------------------------------------------------
    # IMPORTANT
    #
    # Do NOT call:
    #
    #     AngelClient.login()
    #
    # here.
    #
    # LiveManager -> LiveClient -> AngelClient.get_client()
    # handles broker authentication.
    #
    # Starting the live manager in a background thread also
    # prevents broker connection/history initialization from
    # blocking FastAPI startup.
    # ---------------------------------------------------------

    live_manager_task = asyncio.create_task(
        _start_live_manager(),
    )

    logger.info(
        "TradePilot AI started. "
        "Live manager initialization is running in background.",
    )

    # ---------------------------------------------------------
    # FastAPI is now ready.
    # Frontend can connect to /ws/market.
    # ---------------------------------------------------------

    yield

    # =========================================================
    # SHUTDOWN
    # =========================================================

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

    # ---------------------------------------------------------
    # Cancel the asyncio wrapper if it is still waiting.
    #
    # The actual LiveManager worker thread is daemonized.
    # ---------------------------------------------------------

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
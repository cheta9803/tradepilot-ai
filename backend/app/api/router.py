from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.auth.api import router as auth_router
from app.indicators.api import router as indicator_router
from app.instruments.api import router as instruments_router
from app.market.api import router as market_router
from app.strategy.api import router as strategy_router
from app.watchlist.api import router as watchlist_router
from app.live.api import router as live_router
from app.candles.api import router as candles_router
from app.candles.test_api import router as candles_test_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(indicator_router)
api_router.include_router(instruments_router)
api_router.include_router(market_router)
api_router.include_router(strategy_router)
api_router.include_router(watchlist_router)
api_router.include_router(live_router)
api_router.include_router(candles_router)
api_router.include_router(candles_test_router)
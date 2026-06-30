from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.market.api import router as market_router
from app.indicators.api import router as indicator_router
from app.strategy.api import router as strategy_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(market_router)
api_router.include_router(indicator_router)
api_router.include_router(strategy_router)
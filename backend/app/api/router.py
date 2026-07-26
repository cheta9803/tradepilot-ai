from fastapi import APIRouter

from app.account.router import router as account_router
from app.api.v1.health import router as health_router
from app.auth.api import router as auth_router
from app.candles.api import router as candles_router
from app.candles.test_api import router as candles_test_router
from app.indicators.api import router as indicator_router
from app.indicators.test_api import router as indicator_test_router
from app.instruments.api import router as instruments_router
from app.live.api import router as live_router
from app.market.api import router as market_router
from app.orders.router import router as orders_router
from app.portfolio.api import router as portfolio_router
from app.portfolio.router import router as portfolio_summary_router
from app.strategy.api import router as strategy_router
from app.trades.api import router as trades_router
from app.watchlist.api import router as watchlist_router

from app.dashboard.api import router as dashboard_router

api_router = APIRouter(prefix="/api/v1")

# Health
api_router.include_router(health_router)

# Dashboard
api_router.include_router(dashboard_router)

# Authentication
api_router.include_router(auth_router)

# Market Data
api_router.include_router(instruments_router)
api_router.include_router(market_router)
api_router.include_router(watchlist_router)
api_router.include_router(live_router)

# Candle APIs
api_router.include_router(candles_router)
api_router.include_router(candles_test_router)

# Indicator APIs
api_router.include_router(indicator_router)
api_router.include_router(indicator_test_router)

# Strategy & Trade APIs
api_router.include_router(strategy_router)
api_router.include_router(trades_router)

# Portfolio APIs
api_router.include_router(portfolio_router)
api_router.include_router(portfolio_summary_router)

# Account APIs
api_router.include_router(account_router)

# Orders APIs (v1.6.3)
api_router.include_router(orders_router)
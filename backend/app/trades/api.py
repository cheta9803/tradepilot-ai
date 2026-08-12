from fastapi import APIRouter

from app.trades.service import TradeService
from app.trades.history_repository import TradeHistoryRepository

router = APIRouter(
    prefix="/trades",
    tags=["Trades"],
)


@router.get("")
def get_all_trades():

    return TradeService.get_all()


@router.get("/open")
def get_open_trades():

    return TradeService.get_open()


@router.get("/closed")
def get_closed_trades():

    return TradeService.get_closed()

@router.get("/history/daily")
def get_daily_pnl_history():

    return TradeHistoryRepository.get_daily_pnl()

@router.get("/history/daily/{trading_date}")
def get_daily_pnl_trades(
    trading_date: str,
):
    return TradeHistoryRepository.get_day_trades(
        trading_date
    )

@router.get("/{symbol}")
def get_symbol_trades(
    symbol: str,
):

    return TradeService.get_symbol(symbol)
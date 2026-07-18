from fastapi import APIRouter

from app.trades.service import TradeService

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


@router.get("/{symbol}")
def get_symbol_trades(
    symbol: str,
):

    return TradeService.get_symbol(symbol)
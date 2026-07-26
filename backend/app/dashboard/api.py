from fastapi import APIRouter

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("")
async def get_dashboard():
    return {
        "summary": {
            "portfolioValue": 152340,
            "todayPnL": 2340,
            "availableMargin": 45000,
            "openPositions": 3,
        },
        "indices": [
            {
                "name": "NIFTY 50",
                "value": 25186.40,
                "change": 118.35,
                "changePercent": 0.47,
            },
            {
                "name": "BANK NIFTY",
                "value": 56632.15,
                "change": -62.40,
                "changePercent": -0.11,
            },
            {
                "name": "FINNIFTY",
                "value": 27492.20,
                "change": 58.75,
                "changePercent": 0.21,
            },
        ],
        "positions": [
            {
                "symbol": "RELIANCE",
                "quantity": 20,
                "averagePrice": 2700,
                "ltp": 2725,
                "pnl": 500,
            },
            {
                "symbol": "TCS",
                "quantity": 15,
                "averagePrice": 3650,
                "ltp": 3605,
                "pnl": -675,
            },
        ],
        "orders": [
            {
                "symbol": "RELIANCE",
                "type": "BUY",
                "quantity": 20,
                "status": "Completed",
            },
            {
                "symbol": "TCS",
                "type": "SELL",
                "quantity": 10,
                "status": "Pending",
            },
        ],
    }
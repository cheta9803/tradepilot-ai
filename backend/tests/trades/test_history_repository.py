from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.trades.db_models import TradeHistory
from app.trades.history_repository import TradeHistoryRepository


def test_get_daily_pnl():

    db = SessionLocal()

    try:
        rows = (
            db.query(TradeHistory)
            .filter(
                TradeHistory.order_id.in_(
                    [
                        "TEST-DAILY-PNL-1",
                        "TEST-DAILY-PNL-2",
                        "TEST-DAILY-PNL-3",
                    ]
                )
            )
            .all()
        )

        for row in rows:
            db.delete(row)

        db.commit()

        db.add_all(
            [
                TradeHistory(
                    exchange="NSE",
                    token="TEST1",
                    symbol="TEST1",
                    timeframe="1m",
                    signal="BUY",
                    quantity=10,
                    entry_price=100.0,
                    exit_price=110.0,
                    pnl=100.0,
                    reason="TARGET",
                    opened_at=datetime.now(timezone.utc),
                    closed_at=datetime.now(timezone.utc),
                    order_id="TEST-DAILY-PNL-1",
                    execution_mode="PAPER",
                ),
                TradeHistory(
                    exchange="NSE",
                    token="TEST2",
                    symbol="TEST2",
                    timeframe="1m",
                    signal="BUY",
                    quantity=10,
                    entry_price=100.0,
                    exit_price=95.0,
                    pnl=-50.0,
                    reason="STOPLOSS",
                    opened_at=datetime.now(timezone.utc),
                    closed_at=datetime.now(timezone.utc),
                    order_id="TEST-DAILY-PNL-2",
                    execution_mode="PAPER",
                ),
                TradeHistory(
                    exchange="NSE",
                    token="TEST3",
                    symbol="TEST3",
                    timeframe="1m",
                    signal="BUY",
                    quantity=10,
                    entry_price=100.0,
                    exit_price=105.0,
                    pnl=50.0,
                    reason="TARGET",
                    opened_at=datetime.now(timezone.utc),
                    closed_at=datetime.now(timezone.utc),
                    order_id="TEST-DAILY-PNL-3",
                    execution_mode="PAPER",
                ),
            ]
        )

        db.commit()

    finally:
        db.close()

    try:
        result = TradeHistoryRepository.get_daily_pnl()

        assert len(result) >= 1

        today = result[0]

        assert today["tradeCount"] >= 3
        assert today["winningTrades"] >= 2
        assert today["losingTrades"] >= 1
        assert today["grossProfit"] >= 150.0
        assert today["grossLoss"] >= 50.0
        assert today["netPnl"] >= 100.0

    finally:
        db = SessionLocal()

        try:
            db.query(TradeHistory).filter(
                TradeHistory.order_id.in_(
                    [
                        "TEST-DAILY-PNL-1",
                        "TEST-DAILY-PNL-2",
                        "TEST-DAILY-PNL-3",
                    ]
                )
            ).delete(
                synchronize_session=False
            )

            db.commit()

        finally:
            db.close()
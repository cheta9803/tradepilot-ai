from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.trades.db_models import TradeHistory
from app.trades.history_repository import TradeHistoryRepository


TEST_ORDER_IDS = [
    "TEST-DAILY-PNL-1",
    "TEST-DAILY-PNL-2",
    "TEST-DAILY-PNL-3",
]


def test_get_daily_pnl():

    test_date = datetime(
        2099,
        1,
        1,
        10,
        0,
        tzinfo=timezone.utc,
    )

    db = SessionLocal()

    try:

        rows = (
            db.query(TradeHistory)
            .filter(
                TradeHistory.order_id.in_(
                    TEST_ORDER_IDS
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
                    opened_at=test_date,
                    closed_at=test_date,
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
                    opened_at=test_date,
                    closed_at=test_date,
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
                    opened_at=test_date,
                    closed_at=test_date,
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

        test_day = next(
            row
            for row in result
            if row["date"] == "2099-01-01"
        )

        assert test_day["tradeCount"] == 3
        assert test_day["winningTrades"] == 2
        assert test_day["losingTrades"] == 1
        assert test_day["grossProfit"] == 150.0
        assert test_day["grossLoss"] == 50.0
        assert test_day["netPnl"] == 100.0

    finally:

        db = SessionLocal()

        try:

            db.query(TradeHistory).filter(
                TradeHistory.order_id.in_(
                    TEST_ORDER_IDS
                )
            ).delete(
                synchronize_session=False
            )

            db.commit()

        finally:
            db.close()

def test_get_latest_closed_trade():

    test_order_ids = [
        "TEST-LATEST-1",
        "TEST-LATEST-2",
    ]

    test_date_1 = datetime(
        2099,
        1,
        1,
        10,
        0,
        tzinfo=timezone.utc,
    )
    test_date_2 = datetime(
        2099,
        1,
        1,
        10,
        5,
        tzinfo=timezone.utc,
    )

    db = SessionLocal()

    try:
        db.query(TradeHistory).filter(
            TradeHistory.order_id.in_(test_order_ids)
        ).delete(synchronize_session=False)

        db.add_all(
            [
                TradeHistory(
                    exchange="NSE",
                    token="TEST-LATEST",
                    symbol="TEST-LATEST",
                    timeframe="1m",
                    signal="BUY",
                    quantity=10,
                    entry_price=100.0,
                    exit_price=99.0,
                    pnl=-10.0,
                    reason="STOPLOSS",
                    opened_at=test_date_1,
                    closed_at=test_date_1,
                    order_id=test_order_ids[0],
                    execution_mode="PAPER",
                ),
                TradeHistory(
                    exchange="NSE",
                    token="TEST-LATEST",
                    symbol="TEST-LATEST",
                    timeframe="1m",
                    signal="BUY",
                    quantity=10,
                    entry_price=100.0,
                    exit_price=102.0,
                    pnl=20.0,
                    reason="TARGET",
                    opened_at=test_date_2,
                    closed_at=test_date_2,
                    order_id=test_order_ids[1],
                    execution_mode="PAPER",
                ),
            ]
        )
        db.commit()
    finally:
        db.close()

    try:
        latest = TradeHistoryRepository.get_latest_closed_trade(
            exchange="NSE",
            token="TEST-LATEST",
            timeframe="1m",
        )
        assert latest is not None
        assert latest.order_id == "TEST-LATEST-2"
        assert latest.pnl == 20.0
    finally:
        db = SessionLocal()
        try:
            db.query(TradeHistory).filter(
                TradeHistory.order_id.in_(test_order_ids)
            ).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()

from datetime import datetime

from app.db.session import SessionLocal
from app.trades.db_models import TradeHistory


class TradeHistoryRepository:

    @classmethod
    def create_from_trade(
        cls,
        trade: dict,
    ) -> None:

        order_id = trade.get("order_id")

        db = SessionLocal()

        try:

            # Prevent duplicate history records.
            if order_id:

                existing = (
                    db.query(TradeHistory)
                    .filter(
                        TradeHistory.order_id == order_id
                    )
                    .first()
                )

                if existing is not None:
                    return

            closed_at = trade.get("closed_at")

            if closed_at is None:
                return

            if isinstance(closed_at, str):
                closed_at = datetime.fromisoformat(
                    closed_at
                )

            opened_at = trade.get("opened_at")

            if isinstance(opened_at, str):
                opened_at = datetime.fromisoformat(
                    opened_at
                )

            history = TradeHistory(
                exchange=trade["exchange"],
                token=trade["token"],
                symbol=trade["symbol"],
                timeframe=trade["timeframe"],
                signal=trade["signal"],
                quantity=trade["quantity"],
                entry_price=trade["entry_price"],
                exit_price=trade["exit_price"],
                pnl=trade.get("pnl", 0.0),
                reason=trade.get("reason"),
                opened_at=opened_at,
                closed_at=closed_at,
                order_id=order_id,
                execution_mode=trade.get(
                    "execution_mode",
                    "PAPER",
                ),
            )

            db.add(history)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    @classmethod
    def get_today_realized_pnl(
        cls,
    ) -> float:

        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo

        from sqlalchemy import func

        market_tz = ZoneInfo("Asia/Kolkata")

        now = datetime.now(market_tz)

        start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        end = start + timedelta(days=1)

        db = SessionLocal()

        try:

            result = (
                db.query(
                    func.coalesce(
                        func.sum(TradeHistory.pnl),
                        0.0,
                    )
                )
                .filter(
                    TradeHistory.closed_at >= start,
                    TradeHistory.closed_at < end,
                )
                .scalar()
            )

            return round(
                float(result or 0.0),
                2,
            )

        finally:

            db.close()
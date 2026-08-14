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
    def _today_window(cls):

        from datetime import timedelta
        from zoneinfo import ZoneInfo

        market_tz = ZoneInfo("Asia/Kolkata")
        now = datetime.now(market_tz)

        start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        end = start + timedelta(days=1)

        return start, end

    @classmethod
    def get_today_realized_pnl(
        cls,
    ) -> float:

        from sqlalchemy import func

        start, end = cls._today_window()

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

    @classmethod
    def get_today_gross_loss(
        cls,
    ) -> float:

        from sqlalchemy import case, func

        start, end = cls._today_window()

        gross_loss = func.coalesce(
            func.sum(
                case(
                    (
                        TradeHistory.pnl < 0,
                        -TradeHistory.pnl,
                    ),
                    else_=0.0,
                )
            ),
            0.0,
        )

        db = SessionLocal()

        try:

            result = (
                db.query(gross_loss)
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

    @classmethod
    def get_today_loss_streak(
        cls,
    ) -> tuple[int, datetime | None]:
        """
        Return today's consecutive losing-trade streak.

        The first tuple value is the number of consecutive losing
        completed trades, starting from the most recent completed trade.
        The second value is the close time of the most recent trade when
        that streak exists.

        A profitable or break-even trade resets the consecutive-loss streak.
        """

        start, end = cls._today_window()

        db = SessionLocal()

        try:

            rows = (
                db.query(TradeHistory.pnl, TradeHistory.closed_at)
                .filter(
                    TradeHistory.closed_at >= start,
                    TradeHistory.closed_at < end,
                )
                .order_by(
                    TradeHistory.closed_at.desc(),
                    TradeHistory.id.desc(),
                )
                .all()
            )

            streak = 0
            latest_loss_at = None

            for pnl, closed_at in rows:

                if float(pnl or 0.0) >= 0:
                    break

                streak += 1

                if latest_loss_at is None:
                    latest_loss_at = closed_at

            return streak, latest_loss_at

        finally:
            db.close()


    @classmethod
    def get_latest_closed_trade(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> TradeHistory | None:
        """Return the most recent completed trade for an instrument/timeframe."""

        db = SessionLocal()

        try:
            return (
                db.query(TradeHistory)
                .filter(
                    TradeHistory.exchange == exchange,
                    TradeHistory.token == token,
                    TradeHistory.timeframe == timeframe,
                )
                .order_by(
                    TradeHistory.closed_at.desc(),
                    TradeHistory.id.desc(),
                )
                .first()
            )
        finally:
            db.close()

    @classmethod
    def get_daily_pnl(
        cls,
    ) -> list[dict]:

        from sqlalchemy import case, func

        market_timezone = "Asia/Kolkata"

        trading_date = func.date(
            func.timezone(
                market_timezone,
                TradeHistory.closed_at,
            )
        )

        trade_count = func.count(
            TradeHistory.id
        )

        winning_trades = func.sum(
            case(
                (
                    TradeHistory.pnl > 0,
                    1,
                ),
                else_=0,
            )
        )

        losing_trades = func.sum(
            case(
                (
                    TradeHistory.pnl < 0,
                    1,
                ),
                else_=0,
            )
        )

        gross_profit = func.coalesce(
            func.sum(
                case(
                    (
                        TradeHistory.pnl > 0,
                        TradeHistory.pnl,
                    ),
                    else_=0.0,
                )
            ),
            0.0,
        )

        gross_loss = func.coalesce(
            func.sum(
                case(
                    (
                        TradeHistory.pnl < 0,
                        -TradeHistory.pnl,
                    ),
                    else_=0.0,
                )
            ),
            0.0,
        )

        net_pnl = func.coalesce(
            func.sum(
                TradeHistory.pnl
            ),
            0.0,
        )

        db = SessionLocal()

        try:

            rows = (
                db.query(
                    trading_date.label("date"),
                    trade_count.label("trade_count"),
                    winning_trades.label(
                        "winning_trades"
                    ),
                    losing_trades.label(
                        "losing_trades"
                    ),
                    gross_profit.label(
                        "gross_profit"
                    ),
                    gross_loss.label(
                        "gross_loss"
                    ),
                    net_pnl.label("net_pnl"),
                )
                .group_by(
                    trading_date
                )
                .order_by(
                    trading_date.desc()
                )
                .all()
            )

            return [
                {
                    "date": row.date.isoformat(),
                    "tradeCount": int(
                        row.trade_count
                    ),
                    "winningTrades": int(
                        row.winning_trades or 0
                    ),
                    "losingTrades": int(
                        row.losing_trades or 0
                    ),
                    "grossProfit": round(
                        float(
                            row.gross_profit or 0.0
                        ),
                        2,
                    ),
                    "grossLoss": round(
                        float(
                            row.gross_loss or 0.0
                        ),
                        2,
                    ),
                    "netPnl": round(
                        float(
                            row.net_pnl or 0.0
                        ),
                        2,
                    ),
                }
                for row in rows
            ]

        finally:

            db.close()

    @classmethod
    def get_day_trades(
        cls,
        trading_date: str,
    ) -> list[dict]:

        from datetime import date, datetime, time, timedelta
        from zoneinfo import ZoneInfo

        market_tz = ZoneInfo(
            "Asia/Kolkata"
        )

        selected_date = date.fromisoformat(
            trading_date
        )

        start = datetime.combine(
            selected_date,
            time.min,
            tzinfo=market_tz,
        )

        end = start + timedelta(
            days=1
        )

        db = SessionLocal()

        try:

            rows = (
                db.query(
                    TradeHistory
                )
                .filter(
                    TradeHistory.closed_at >= start,
                    TradeHistory.closed_at < end,
                )
                .order_by(
                    TradeHistory.closed_at.desc()
                )
                .all()
            )

            return [
                {
                    "time": (
                        row.closed_at
                        .astimezone(market_tz)
                        .isoformat()
                    ),
                    "symbol": row.symbol,
                    "side": row.signal,
                    "quantity": row.quantity,
                    "entryPrice": round(
                        float(
                            row.entry_price
                        ),
                        2,
                    ),
                    "exitPrice": round(
                        float(
                            row.exit_price
                        ),
                        2,
                    ),
                    "pnl": round(
                        float(row.pnl),
                        2,
                    ),
                    "reason": row.reason,
                }
                for row in rows
            ]

        finally:

            db.close()

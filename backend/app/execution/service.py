
from app.core.config import settings
from app.core.logger import logger
from app.core.market_session import MarketSession
from app.execution.eod import EndOfDayService
from app.execution.order_service import ExecutionOrderService
from app.live.redis_cache import LiveCache
from app.risk.engine import RiskEngine
from app.trades.lifecycle import TradeLifecycle
from app.trades.service import TradeService


class ExecutionService:

    @classmethod
    def process(cls) -> None:

        trades = TradeService.get_open()

        market_open = MarketSession.can_enter_trade()

        for trade in trades:

            live = LiveCache.get(
                trade["token"]
            )

            if live is None:
                continue

            ltp = live["ltp"]

            state = trade["state"]

            #
            # New trade execution
            #
            if (
                state == "ENTRY_READY"
                and market_open
            ):

                cls._process_entry(
                    trade,
                    ltp,
                )

            #
            # Active trade management
            #
            elif state in (
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            ):

                cls._update_live_pnl(
                    trade,
                    ltp,
                )

                RiskEngine.process(
                    trade=trade,
                    ltp=ltp,
                )

                #
                # Risk engine may have modified
                # stoploss/trailing state.
                #
                trade = TradeLifecycle.get(
                    exchange=trade["exchange"],
                    token=trade["token"],
                    timeframe=trade["timeframe"],
                )

                if trade is None:
                    continue

                cls._process_exit(
                    trade,
                    ltp,
                )

        if MarketSession.should_square_off():
            EndOfDayService.square_off()

    @classmethod
    def _update_live_pnl(
        cls,
        trade: dict,
        ltp: float,
    ) -> None:

        if trade["signal"] == "BUY":

            pnl = (
                ltp
                - trade["entry_price"]
            ) * trade["quantity"]

        else:

            pnl = (
                trade["entry_price"]
                - ltp
            ) * trade["quantity"]

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values={
                "current_price": round(
                    ltp,
                    2,
                ),
                "pnl": round(
                    pnl,
                    2,
                ),
            },
        )

    @classmethod
    def _process_entry(
        cls,
        trade: dict,
        ltp: float,
    ) -> None:

        #
        # Never retry failed live orders.
        #
        if (
            trade.get("execution_mode") == "LIVE"
            and trade.get("order_status") == "FAILED"
        ):
            return

        #
        # Live broker execution must be explicitly enabled.
        #
        if (
            not settings.paper_trading
            and not settings.live_trading_enabled
        ):
            logger.warning(
                "Live trading disabled. "
                "Blocking entry for %s %s.",
                trade["symbol"],
                trade["timeframe"],
            )

            TradeLifecycle.update(
                exchange=trade["exchange"],
                token=trade["token"],
                timeframe=trade["timeframe"],
                values={
                    "state": "EXECUTION_BLOCKED",
                    "reason": "LIVE_TRADING_DISABLED",
                },
            )

            return

        signal = trade["signal"]

        activate = False

        if (
            signal == "BUY"
            and ltp >= trade["entry_price"]
        ):
            activate = True

        elif (
            signal == "SELL"
            and ltp <= trade["entry_price"]
        ):
            activate = True

        if not activate:
            return

        success = ExecutionOrderService.execute_entry(
            trade
        )

        if not success:

            TradeLifecycle.update(
                exchange=trade["exchange"],
                token=trade["token"],
                timeframe=trade["timeframe"],
                values={
                    "state": "ENTRY_FAILED",
                    "reason": "BROKER_ORDER_FAILED",
                },
            )

            return

        print(
            f"Trade Activated "
            f"{trade['symbol']} "
            f"{trade['timeframe']}"
        )

    @classmethod
    def _process_exit(
        cls,
        trade: dict,
        ltp: float,
    ) -> None:

        if trade["closed_at"] is not None:
            return

        signal = trade["signal"]

        exit_reason = None

        if signal == "BUY":

            if ltp >= trade["target"]:
                exit_reason = "TARGET"

            elif ltp <= trade["stop_loss"]:
                exit_reason = "STOPLOSS"

        else:

            if ltp <= trade["target"]:
                exit_reason = "TARGET"

            elif ltp >= trade["stop_loss"]:
                exit_reason = "STOPLOSS"

        if exit_reason is None:
            return

        pnl = (
            ltp
            - trade["entry_price"]
        ) * trade["quantity"]

        if signal == "SELL":
            pnl *= -1

        TradeLifecycle.update(
            exchange=trade["exchange"],
            token=trade["token"],
            timeframe=trade["timeframe"],
            values={
                "state": "EXIT",
                "exit_price": round(
                    ltp,
                    2,
                ),
                "current_price": round(
                    ltp,
                    2,
                ),
                "reason": exit_reason,
                "pnl": round(
                    pnl,
                    2,
                ),
            },
        )

        print(
            f"Trade Closed "
            f"{trade['symbol']} "
            f"{exit_reason}"
        )
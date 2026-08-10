from app.core.config import settings
from app.core.market_session import MarketSession

from app.indicators.cache import IndicatorCache
from app.instruments.cache import InstrumentCache
from app.live.redis_cache import LiveCache
from app.history.redis_cache import HistoryCache
from app.pretrade.engine import PreTradeRiskEngine
from app.strategy.cache import StrategyCache
from app.strategy.position import PositionSizer
from app.strategy.risk import RiskManager
from app.strategy.rules import StrategyRules
from app.strategy.state import TradeState
from app.strategy.trend import TrendService
from app.trades.cache import TradeCache
from app.trades.lifecycle import TradeLifecycle
from app.patterns.cache import PatternCache


class StrategyEngine:

    @classmethod
    def calculate(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> None:

        instrument = InstrumentCache.get_by_token(
            token
        )

        if instrument is None:
            return

        candles = HistoryCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if not candles:
            return

        indicators = IndicatorCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        latest_timestamp = candles[-1].timestamp.isoformat()

        # Never use indicators calculated for an older candle series. This is
        # especially important during startup when the DB may contain only a
        # small historical cache and a previous indicator value.
        if (
            indicators is None
            or indicators.get("candle_timestamp") != latest_timestamp
        ):
            print(
                f"Skipping strategy for "
                f"{instrument.symbol} {timeframe}. "
                f"Indicators are not aligned with the latest candle."
            )
            return

        live = LiveCache.get(
            token
        )

        if live is None:
            return

        entry = live["ltp"]

        trend = TrendService.evaluate(
            ema20=indicators["ema20"],
            ema50=indicators["ema50"],
        )

        signal, confidence, reasons = (
            StrategyRules.evaluate(
                ema20=indicators["ema20"],
                rsi=indicators["rsi14"],
                price=entry,
                vwap=indicators["vwap"],
                macd=indicators["macd"],
                signal=indicators["signal"],
            )
        )

        #
        # Supertrend confirmation
        #
        supertrend_signal = indicators.get(
            "supertrend_signal",
        )

        if (
            signal == StrategyRules.BUY
            and supertrend_signal == "SELL"
        ):

            signal = StrategyRules.HOLD
            confidence = max(
                confidence - 20,
                50,
            )

            reasons.append(
                "Supertrend is SELL"
            )

        elif (
            signal == StrategyRules.SELL
            and supertrend_signal == "BUY"
        ):

            signal = StrategyRules.HOLD
            confidence = max(
                confidence - 20,
                50,
            )

            reasons.append(
                "Supertrend is BUY"
            )

        #
        # Trend Filter
        #
        if (
            trend == TrendService.UPTREND
            and signal == StrategyRules.SELL
        ):

            signal = StrategyRules.HOLD
            confidence = 50

            reasons.append(
                "SELL ignored because overall trend is UPTREND"
            )

        elif (
            trend == TrendService.DOWNTREND
            and signal == StrategyRules.BUY
        ):

            signal = StrategyRules.HOLD
            confidence = 50

            reasons.append(
                "BUY ignored because overall trend is DOWNTREND"
            )

        state = TradeState.evaluate(
            trend=trend,
            signal=signal,
            confidence=confidence,
        )

        stop_loss, target = (
            RiskManager.calculate(
                signal=signal,
                entry=entry,
                atr=indicators["atr14"],
            )
        )

        position = PositionSizer.calculate(
            capital=settings.default_capital,
            entry=entry,
            stop_loss=stop_loss,
        )

        #
        # Always update strategy cache.
        #
        StrategyCache.save(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
            values={
                "exchange": instrument.exchange,
                "token": instrument.token,
                "symbol": instrument.symbol,
                "timeframe": timeframe,
                "trend": trend,
                "state": state,
                "signal": signal,
                "confidence": confidence,
                "tradable": (
                    signal != StrategyRules.HOLD
                ),
                "entry": entry,
                "stop_loss": stop_loss,
                "target": target,
                "risk_reward": 2.0,
                "ema20": indicators["ema20"],
                "ema50": indicators["ema50"],
                "rsi14": indicators["rsi14"],
                "atr14": indicators["atr14"],
                "vwap": indicators["vwap"],
                "macd": indicators["macd"],
                "signal_line": indicators["signal"],
                "supertrend": indicators["supertrend"],
                "supertrend_signal": indicators[
                    "supertrend_signal"
                ],
                "quantity": position["quantity"],
                "invested": position["invested"],
                "risk_amount": position["risk_amount"],
                "reasons": reasons,
            },
        )

        patterns = PatternCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if patterns:

            if patterns["bullish_engulfing"]:

                confidence += 5

                reasons.append(
                    "Bullish Engulfing"
                )

            if patterns["bearish_engulfing"]:

                confidence -= 5

                reasons.append(
                    "Bearish Engulfing"
                )

            if patterns["hammer"]:

                confidence += 3

                reasons.append(
                    "Hammer Pattern"
                )

            if patterns["shooting_star"]:

                confidence -= 3

                reasons.append(
                    "Shooting Star"
                )

            if patterns["breakout"]:

                confidence += 5

                reasons.append(
                    "Breakout"
                )

            if patterns["breakdown"]:

                confidence -= 5

                reasons.append(
                    "Breakdown"
                )

        #
        # No entry signal.
        #
        if state != TradeState.ENTRY_READY:

            print(
                f"Strategy updated "
                f"{instrument.symbol} "
                f"{timeframe}"
            )

            return

        #
        # Never create LIVE trades
        # outside market hours.
        #
        if not MarketSession.can_enter_trade():

            print(
                f"Market closed. "
                f"Skipping trade creation "
                f"{instrument.symbol} "
                f"{timeframe}"
            )

            return

        #
        # Existing active trade?
        #
        existing_trade = TradeCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if (
            existing_trade is not None
            and existing_trade["state"] in (
                "ENTRY_READY",
                "BUY_ACTIVE",
                "SELL_ACTIVE",
            )
        ):

            print(
                f"Trade already exists "
                f"{instrument.symbol} "
                f"{timeframe} "
                f"state={existing_trade['state']}"
            )

            return

        #
        # Risk checks.
        #
        if not PreTradeRiskEngine.can_open_trade():

            print(
                f"Risk check failed "
                f"{instrument.symbol} "
                f"{timeframe}"
            )

            return

        #
        # Create trade.
        #
        # TradeLifecycle.create() will:
        #
        # - ignore active trades
        # - replace completed trades
        # - save the new trade
        #
        TradeLifecycle.create(
            exchange=exchange,
            token=token,
            symbol=instrument.symbol,
            timeframe=timeframe,
            signal=signal,
            state=state,
            entry=entry,
            stop_loss=stop_loss,
            target=target,
            quantity=position["quantity"],
            execution_mode="LIVE",
        )

        print(
            f"Created trade "
            f"{instrument.symbol} "
            f"{timeframe}"
        )
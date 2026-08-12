from app.core.config import settings
from app.core.market_session import MarketSession

from app.indicators.cache import IndicatorCache
from app.instruments.cache import InstrumentCache
from app.live.redis_cache import LiveCache
from app.history.redis_cache import HistoryCache
from app.pretrade.engine import PreTradeRiskEngine
from app.strategy.cache import StrategyCache
from app.strategy.multi_timeframe import MultiTimeframeStrategy
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

        patterns = PatternCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        position = PositionSizer.calculate(
            capital=settings.default_capital,
            entry=entry,
            stop_loss=stop_loss,
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

        state = TradeState.evaluate(
            trend=trend,
            signal=signal,
            confidence=confidence,
        )

        # Pattern adjustments are part of the final strategy confidence.
        # Persist them before the multi-timeframe decision reads this cache.
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
                "tradable": signal != StrategyRules.HOLD,
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
                "supertrend_signal": indicators["supertrend_signal"],
                "quantity": position["quantity"],
                "invested": position["invested"],
                "risk_amount": position["risk_amount"],
                "reasons": reasons,
            },
        )

        #
        # A timeframe strategy is analytical data only.
        # One real intraday trade is created only by the 1m entry trigger
        # after 15m bias + 5m setup + 1m trigger agree.
        #
        if timeframe != "1m":
            print(
                f"Strategy updated {instrument.symbol} {timeframe}; "
                "no independent trade created."
            )
            return

        master = MultiTimeframeStrategy.calculate(
            exchange=exchange,
            token=token,
        )

        if not master["trade_ready"]:
            print(
                f"Multi-timeframe WAIT "
                f"{instrument.symbol}: "
                f"{master['reasons'][0]}"
            )
            return

        signal = master["signal"]
        entry = float(master["entry"])
        stop_loss = float(master["stop_loss"])
        target = float(master["target"])

        position = PositionSizer.calculate(
            capital=settings.default_capital,
            entry=entry,
            stop_loss=stop_loss,
        )

        #
        # Never create LIVE trades outside market hours.
        #
        if not MarketSession.can_enter_trade():
            print(
                f"Market closed. Skipping master trade creation "
                f"{instrument.symbol} 1m"
            )
            return

        existing_trade = TradeCache.get(
            exchange=exchange,
            token=token,
            timeframe="1m",
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
                f"Master trade already exists "
                f"{instrument.symbol} 1m "
                f"state={existing_trade['state']}"
            )
            return

        if not PreTradeRiskEngine.can_open_trade():
            print(
                f"Risk check failed {instrument.symbol} master 1m"
            )
            return

        TradeLifecycle.create(
            exchange=exchange,
            token=token,
            symbol=instrument.symbol,
            timeframe="1m",
            signal=signal,
            state=TradeState.ENTRY_READY,
            entry=entry,
            stop_loss=stop_loss,
            target=target,
            quantity=position["quantity"],
            execution_mode=(
                "PAPER"
                if settings.paper_trading
                else "LIVE"
            ),
        )

        print(
            f"Created master trade "
            f"{instrument.symbol} 1m "
            f"signal={signal} "
            f"confidence={master['confidence']} "
            f"entry={entry} "
            f"stop={stop_loss} "
            f"target={target}"
        )

from app.core.market_session import MarketSession
from app.indicators.engine import IndicatorEngine
from app.history.redis_cache import HistoryCache
from app.indicators.cache import IndicatorCache
from app.instruments.cache import InstrumentCache
from app.live.redis_cache import LiveCache
from app.strategy.cache import StrategyCache
from app.strategy.risk import RiskManager
from app.strategy.rules import StrategyRules
from app.strategy.trend import TrendService


class StrategyService:

    @staticmethod
    def _ensure_indicators(
        *,
        symbol: str,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> dict | None:

        candles = HistoryCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        latest_timestamp = (
            candles[-1].timestamp.isoformat()
            if candles
            else None
        )

        indicators = IndicatorCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if (
            indicators is not None
            and latest_timestamp is not None
            and indicators.get("candle_timestamp") == latest_timestamp
        ):
            return indicators

        # The cached indicators may belong to an older session. Recalculate
        # from the current history instead of combining stale indicators with
        # today's live LTP. IndicatorEngine handles history warm-up when needed.
        IndicatorEngine.calculate(
            symbol=symbol,
            timeframe=timeframe,
        )

        return IndicatorCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

    def analyze(
        self,
        symbol: str,
        timeframe: str = "1m",
    ):

        symbol = symbol.upper()

        instrument = InstrumentCache.get_by_symbol(
            exchange="NSE",
            symbol=symbol,
        )

        if instrument is None:

            raise ValueError(
                f"Instrument not found: {symbol}"
            )

        indicators = self._ensure_indicators(
            symbol=symbol,
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe=timeframe,
        )

        if indicators is None:

            raise ValueError(
                f"Indicators not available for "
                f"{symbol} {timeframe}."
            )

        live = LiveCache.get(
            instrument.token,
        )

        historical_analysis = False

        if live is not None:

            latest_price = live["ltp"]

        else:

            #
            # During market hours we still require live data.
            #
            if MarketSession.is_open():

                raise ValueError(
                    "Live price not available."
                )

            #
            # Outside market hours, use the latest historical
            # candle for analysis only.
            #
            candles = HistoryCache.get(
                exchange=instrument.exchange,
                token=instrument.token,
                timeframe=timeframe,
            )

            if not candles:

                raise ValueError(
                    "Historical price not available."
                )

            latest_price = candles[-1].close

            historical_analysis = True

        trend = TrendService.evaluate(
            ema20=indicators["ema20"],
            ema50=indicators["ema50"],
        )

        signal, confidence, reasons = (
            StrategyRules.evaluate(
                ema20=indicators["ema20"],
                ema50=indicators.get("ema50"),
                rsi=indicators["rsi14"],
                price=latest_price,
                vwap=indicators["vwap"],
                macd=indicators["macd"],
                signal=indicators["signal"],
            )
        )

        #
        # Supertrend confirmation.
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
        # Trend filter.
        #
        if (
            trend == TrendService.UPTREND
            and signal == StrategyRules.SELL
        ):

            signal = StrategyRules.HOLD

            confidence = 50

            reasons.append(
                "SELL ignored because overall "
                "trend is UPTREND"
            )

        elif (
            trend == TrendService.DOWNTREND
            and signal == StrategyRules.BUY
        ):

            signal = StrategyRules.HOLD

            confidence = 50

            reasons.append(
                "BUY ignored because overall "
                "trend is DOWNTREND"
            )

        if historical_analysis:

            reasons.append(
                "Market closed; analysis uses "
                "the latest historical candle."
            )

        #
        # Historical analysis must never be considered
        # tradable.
        #
        tradable = (
            signal != StrategyRules.HOLD
            and not historical_analysis
        )

        stop_loss, target = (
            RiskManager.calculate(
                signal=signal,
                entry=latest_price,
                atr=indicators["atr14"],
            )
        )

        result = {
            "exchange": instrument.exchange,
            "token": instrument.token,
            "symbol": symbol,
            "timeframe": timeframe,
            "trend": trend,
            "signal": signal,
            "confidence": confidence,
            "tradable": tradable,
            "entry": latest_price,
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
            "reasons": reasons,
        }

        StrategyCache.save(
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe=timeframe,
            values=result,
        )

        return result
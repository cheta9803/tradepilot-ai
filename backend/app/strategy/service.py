from app.indicators.cache import IndicatorCache
from app.instruments.cache import InstrumentCache
from app.live.redis_cache import LiveCache
from app.strategy.rules import StrategyRules


class StrategyService:

    def analyze(
        self,
        symbol: str,
        timeframe: str = "1m",
    ):

        instrument = InstrumentCache.get_by_symbol(
            exchange="NSE",
            symbol=symbol,
        )

        if instrument is None:
            raise ValueError(
                f"Instrument not found: {symbol}"
            )

        indicators = IndicatorCache.get(
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe=timeframe,
        )

        if indicators is None:
            raise ValueError(
                "Indicators not available."
            )

        live = LiveCache.get(
            instrument.token,
        )

        if live is None:
            raise ValueError(
                "Live price not available."
            )

        latest_price = live["ltp"]

        signal, confidence, reasons = StrategyRules.evaluate(
            ema20=indicators["ema20"],
            rsi=indicators["rsi14"],
            price=latest_price,
            vwap=indicators["vwap"],
            macd=indicators["macd"],
            signal=indicators["signal"],
        )

        atr = indicators["atr14"]

        stop_loss = round(
            latest_price - atr,
            2,
        )

        target = round(
            latest_price + (atr * 2),
            2,
        )

        return {
            "symbol": symbol,
            "timeframe": timeframe,

            "signal": signal,
            "confidence": confidence,

            "entry": latest_price,
            "stop_loss": stop_loss,
            "target": target,
            "risk_reward": 2.0,

            "ema20": indicators["ema20"],
            "rsi14": indicators["rsi14"],
            "atr14": indicators["atr14"],
            "vwap": indicators["vwap"],
            "macd": indicators["macd"],
            "signal_line": indicators["signal"],

            "reasons": reasons,
        }
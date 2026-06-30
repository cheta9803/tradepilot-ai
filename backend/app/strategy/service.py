from app.indicators.calculators.atr import ATRCalculator
from app.indicators.calculators.ema import EMACalculator
from app.indicators.calculators.macd import MACDCalculator
from app.indicators.calculators.rsi import RSICalculator
from app.indicators.calculators.vwap import VWAPCalculator
from app.market.service import MarketService
from app.strategy.rules import StrategyRules


class StrategyService:

    def __init__(self):
        self.market_service = MarketService()

    def analyze(
        self,
        symbol: str,
        timeframe: str = "5m",
    ):
        candles = self.market_service.get_history(
            symbol=symbol,
            timeframe=timeframe,
            limit=100,
        )

        latest_price = candles[-1].close

        ema20 = EMACalculator.calculate(candles, 20)
        ema50 = EMACalculator.calculate(candles, 50)

        rsi = RSICalculator.calculate(candles, 14)

        vwap = VWAPCalculator.calculate(candles)

        atr = ATRCalculator.calculate(candles, 14)

        macd_result = MACDCalculator.calculate(candles)

        signal, confidence, reasons = StrategyRules.evaluate(
            ema20=ema20,
            ema50=ema50,
            rsi=rsi,
            price=latest_price,
            vwap=vwap,
            macd=macd_result["macd"],
            signal=macd_result["signal"],
        )

        stop_loss = round(latest_price - atr, 2)
        target = round(latest_price + (atr * 2), 2)

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": signal,
            "confidence": confidence,
            "entry": latest_price,
            "stop_loss": stop_loss,
            "target": target,
            "risk_reward": 2.0,
            "reasons": reasons,
        }
from app.core.config import settings

from app.execution.engine import ExecutionEngine
from app.indicators.cache import IndicatorCache
from app.instruments.cache import InstrumentCache
from app.live.redis_cache import LiveCache
from app.pretrade.engine import PreTradeRiskEngine
from app.strategy.cache import StrategyCache
from app.strategy.position import PositionSizer
from app.strategy.risk import RiskManager
from app.strategy.rules import StrategyRules
from app.strategy.state import TradeState
from app.strategy.trend import TrendService
from app.trades.lifecycle import TradeLifecycle


class StrategyEngine:

    @classmethod
    def calculate(
        cls,
        *,
        exchange: str,
        token: str,
        timeframe: str,
    ) -> None:

        instrument = InstrumentCache.get_by_token(token)

        if instrument is None:
            return

        indicators = IndicatorCache.get(
            exchange=exchange,
            token=token,
            timeframe=timeframe,
        )

        if indicators is None:
            return

        live = LiveCache.get(token)

        if live is None:
            return

        entry = live["ltp"]

        trend = TrendService.evaluate(
            ema20=indicators["ema20"],
            ema50=indicators["ema50"],
        )

        signal, confidence, reasons = StrategyRules.evaluate(
            ema20=indicators["ema20"],
            rsi=indicators["rsi14"],
            price=entry,
            vwap=indicators["vwap"],
            macd=indicators["macd"],
            signal=indicators["signal"],
        )

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

        stop_loss, target = RiskManager.calculate(
            signal=signal,
            entry=entry,
            atr=indicators["atr14"],
        )

        position = PositionSizer.calculate(
            capital=settings.default_capital,
            entry=entry,
            stop_loss=stop_loss,
        )

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
                "quantity": position["quantity"],
                "invested": position["invested"],
                "risk_amount": position["risk_amount"],
                "reasons": reasons,
            },
        )

        if state == TradeState.ENTRY_READY:

            if not PreTradeRiskEngine.can_open_trade():
                return

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

            ExecutionEngine.process()

        print(
            f"Strategy updated "
            f"{instrument.symbol} "
            f"{timeframe}"
        )
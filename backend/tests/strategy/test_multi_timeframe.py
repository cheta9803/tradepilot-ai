from app.strategy.multi_timeframe import MultiTimeframeStrategy


class TestMultiTimeframeStrategy:

    @staticmethod
    def _strategy(
        signal,
        confidence,
        entry=100.0,
        atr=2.0,
        entry_trigger=False,
        entry_trigger_reason=None,
    ):
        return {
            "signal": signal,
            "confidence": confidence,
            "entry": entry,
            "atr14": atr,
            "entry_trigger": entry_trigger,
            "entry_trigger_reason": entry_trigger_reason,
        }

    def test_buy_requires_15m_direction_5m_setup_and_1m_trigger(self, monkeypatch):
        values = {
            "15m": self._strategy("BUY", 80),
            "5m": self._strategy("BUY", 75, atr=3.0),
            "1m": self._strategy(
                "BUY",
                70,
                entry=101.0,
                entry_trigger=True,
                entry_trigger_reason="1m bullish breakout confirmed",
            ),
        }

        monkeypatch.setattr(
            "app.strategy.multi_timeframe.StrategyCache.get",
            lambda **kwargs: values.get(kwargs["timeframe"]),
        )

        result = MultiTimeframeStrategy.calculate(
            exchange="NSE",
            token="123",
        )

        assert result["signal"] == "BUY"
        assert result["recommendation"] == "BUY"
        assert result["trade_ready"] is True
        assert result["confidence"] == 76
        assert result["entry"] == 101.0
        assert result["stop_loss"] == 98.0
        assert result["target"] == 107.0
        assert result["atr_5m"] == 3.0
        assert result["entry_trigger"] is True

    def test_aligned_timeframes_without_1m_trigger_means_wait(self, monkeypatch):
        values = {
            "15m": self._strategy("BUY", 80),
            "5m": self._strategy("BUY", 75, atr=3.0),
            "1m": self._strategy("BUY", 90, entry=101.0),
        }

        monkeypatch.setattr(
            "app.strategy.multi_timeframe.StrategyCache.get",
            lambda **kwargs: values.get(kwargs["timeframe"]),
        )

        result = MultiTimeframeStrategy.calculate(
            exchange="NSE",
            token="123",
        )

        assert result["recommendation"] == "WAIT"
        assert result["trade_ready"] is False
        assert result["entry"] is None
        assert "entry trigger" in result["reasons"][0].lower()

    def test_timeframe_conflict_means_wait(self, monkeypatch):
        values = {
            "15m": self._strategy("BUY", 85),
            "5m": self._strategy("SELL", 80, atr=3.0),
            "1m": self._strategy("BUY", 90, entry_trigger=True),
        }

        monkeypatch.setattr(
            "app.strategy.multi_timeframe.StrategyCache.get",
            lambda **kwargs: values.get(kwargs["timeframe"]),
        )

        result = MultiTimeframeStrategy.calculate(
            exchange="NSE",
            token="123",
        )

        assert result["recommendation"] == "WAIT"
        assert result["trade_ready"] is False
        assert result["signal"] == "HOLD"
        assert result["entry"] is None

    def test_low_confidence_means_wait(self, monkeypatch):
        values = {
            "15m": self._strategy("BUY", 80),
            "5m": self._strategy("BUY", 69, atr=3.0),
            "1m": self._strategy("BUY", 90, entry_trigger=True),
        }

        monkeypatch.setattr(
            "app.strategy.multi_timeframe.StrategyCache.get",
            lambda **kwargs: values.get(kwargs["timeframe"]),
        )

        result = MultiTimeframeStrategy.calculate(
            exchange="NSE",
            token="123",
        )

        assert result["recommendation"] == "WAIT"
        assert result["trade_ready"] is False

    def test_missing_timeframe_means_wait(self, monkeypatch):
        values = {
            "15m": self._strategy("BUY", 80),
            "5m": self._strategy("BUY", 80, atr=3.0),
        }

        monkeypatch.setattr(
            "app.strategy.multi_timeframe.StrategyCache.get",
            lambda **kwargs: values.get(kwargs["timeframe"]),
        )

        result = MultiTimeframeStrategy.calculate(
            exchange="NSE",
            token="123",
        )

        assert result["recommendation"] == "WAIT"
        assert result["trade_ready"] is False
        assert result["signals"]["1m"] == "UNKNOWN"

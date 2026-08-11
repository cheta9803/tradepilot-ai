from app.ai.service import AIService


class TestAIService:

    def test_top_opportunities_prioritizes_actionable_results(self, monkeypatch):
        values = {
            "strategy:NSE:26000:1m": {},
            "strategy:NSE:26009:1m": {},
            "strategy:NSE:26037:1m": {},
        }

        class FakeRedis:
            def scan_iter(self, match):
                assert match == "strategy:*:1m"
                return list(values.keys())

        monkeypatch.setattr(
            "app.ai.service.redis_client",
            FakeRedis(),
            raising=False,
        )

        # AIService imports redis_client lazily from app.db.redis, so patch the
        # module object used by that import.
        import sys

        monkeypatch.setitem(
            sys.modules,
            "app.db.redis",
            type("RedisModule", (), {"redis_client": FakeRedis()}),
        )

        strategies = {
            "26000": {"trend": "UPTREND", "entry": 100, "ema20": 90, "rsi14": 60, "macd": 2, "signal_line": 1, "supertrend_signal": "BUY", "vwap": 95},
            "26009": {"trend": "UPTREND", "entry": 100, "ema20": 90, "rsi14": 60, "macd": 2, "signal_line": 1, "supertrend_signal": "BUY", "vwap": 95},
            "26037": {"trend": "UPTREND", "entry": 100, "ema20": 90, "rsi14": 60, "macd": 2, "signal_line": 1, "supertrend_signal": "BUY", "vwap": 95},
        }

        monkeypatch.setattr(
            "app.ai.service.StrategyCache.get",
            lambda **kwargs: strategies[kwargs["token"]],
        )
        monkeypatch.setattr(
            "app.ai.service.PatternCache.get",
            lambda **kwargs: None,
        )

        confirmations = {
            "26000": {"trade_ready": False, "signal": "HOLD", "confidence": 0, "signals": {"15m": "BUY", "5m": "SELL", "1m": "BUY"}, "confidences": {}, "entry": None, "stop_loss": None, "target": None, "risk_reward": 2.0, "reasons": ["Conflict"]},
            "26009": {"trade_ready": True, "signal": "BUY", "confidence": 86, "signals": {"15m": "BUY", "5m": "BUY", "1m": "BUY"}, "confidences": {"15m": 90, "5m": 85, "1m": 80}, "entry": 100, "stop_loss": 97, "target": 106, "risk_reward": 2.0, "reasons": ["Aligned"]},
            "26037": {"trade_ready": False, "signal": "HOLD", "confidence": 0, "signals": {"15m": "BUY", "5m": "BUY", "1m": "HOLD"}, "confidences": {}, "entry": None, "stop_loss": None, "target": None, "risk_reward": 2.0, "reasons": ["Conflict"]},
        }

        monkeypatch.setattr(
            "app.ai.service.TimeframeConfirmation.calculate",
            lambda **kwargs: confirmations[kwargs["token"]],
        )
        monkeypatch.setattr(
            "app.ai.service.InstrumentCache.get_by_token",
            staticmethod(
                lambda token: type(
                    "Instrument", (), {"symbol": f"TEST{token}"}
                )()
            ),
        )

        result = AIService.top_opportunities(limit=3)

        assert result[0]["token"] == "26009"
        assert result[0]["trade_ready"] is True
        assert result[0]["recommendation"] == "BUY"
        assert result[1]["recommendation"] == "WAIT"

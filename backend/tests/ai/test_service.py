from app.ai.service import AIService


class TestAIService:

    def test_top_opportunities_ranks_by_confidence(self, monkeypatch):
        class FakeRedis:
            def __init__(self):
                self._values = {
                    "ai:NSE:26000:1m": '{"score": 20, "confidence": 20, "recommendation": "HOLD"}',
                    "ai:NSE:26009:1m": '{"score": 80, "confidence": 80, "recommendation": "BUY"}',
                    "ai:NSE:26037:1m": '{"score": 60, "confidence": 60, "recommendation": "WATCH"}',
                }

            def scan_iter(self, match):
                return list(self._values.keys())

            def get(self, key):
                return self._values.get(key)

        fake_redis = FakeRedis()

        monkeypatch.setitem(
            __import__("sys").modules,
            "app.db.redis",
            type("RedisModule", (), {"redis_client": fake_redis}),
        )

        monkeypatch.setitem(
            __import__("sys").modules,
            "app.instruments.cache",
            type(
                "InstrumentCacheModule",
                (),
                {
                    "InstrumentCache": type(
                        "InstrumentCache",
                        (),
                        {
                            "get_by_token": staticmethod(
                                lambda token: type("Instrument", (), {"symbol": "TEST"})()
                            )
                        },
                    )
                },
            ),
        )

        monkeypatch.setitem(
            __import__("sys").modules,
            "app.strategy.cache",
            type(
                "StrategyCacheModule",
                (),
                {
                    "StrategyCache": type(
                        "StrategyCache",
                        (),
                        {"get": staticmethod(lambda **kwargs: {"trend": "UPTREND", "entry": 100, "ema20": 90, "rsi14": 60, "macd": 2.0, "signal_line": 1.0, "supertrend_signal": "BUY", "vwap": 95, "signal": "BUY"})},
                    )
                },
            ),
        )

        monkeypatch.setitem(
            __import__("sys").modules,
            "app.patterns.cache",
            type(
                "PatternCacheModule",
                (),
                {"PatternCache": type("PatternCache", (), {"get": staticmethod(lambda **kwargs: None)})},
            ),
        )

        result = AIService.top_opportunities(limit=5)

        assert [item["token"] for item in result[:3]] == ["26000", "26009", "26037"]

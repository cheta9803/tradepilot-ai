from app.ai.scorer import AIScorer


class TestAIScorer:

    def test_moderate_bullish_signal_is_ranked_as_watch(self):
        strategy = {
            "trend": "UPTREND",
            "entry": 100,
            "ema20": 95,
            "rsi14": 50,
            "macd": 1.0,
            "signal_line": 2.0,
            "supertrend_signal": "SELL",
            "vwap": 90,
        }

        score = AIScorer.calculate(
            strategy=strategy,
            patterns=None,
        )

        assert score["recommendation"] == "WATCH"
        assert score["score"] >= 25

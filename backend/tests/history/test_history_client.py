from datetime import datetime
from unittest.mock import MagicMock, patch

from app.history.client import HistoryClient


class TestHistoryClient:

    def test_returns_empty_list_when_broker_call_fails(self):
        with patch("app.history.client.AngelClient.login") as login_mock:
            login_mock.side_effect = ValueError("bad response")

            candles = HistoryClient.get_candles(
                exchange="NSE",
                symbol_token="26000",
                interval="ONE_MINUTE",
                from_date=datetime(2024, 1, 1, 0, 0),
                to_date=datetime(2024, 1, 1, 0, 5),
            )

        assert candles == []

    def test_raises_value_error_when_rate_limited(self):
        client_mock = MagicMock()
        client_mock.getCandleData.side_effect = ValueError(
            "Too many requests"
        )

        with patch("app.history.client.AngelClient.login", return_value=client_mock):
            try:
                HistoryClient.get_candles(
                    exchange="NSE",
                    symbol_token="26000",
                    interval="ONE_MINUTE",
                    from_date=datetime(2024, 1, 1, 0, 0),
                    to_date=datetime(2024, 1, 1, 0, 5),
                )
            except ValueError as exc:
                assert str(exc) == "Too many requests"
            else:
                raise AssertionError("Expected rate-limit ValueError")

    def test_returns_empty_list_when_broker_returns_no_data(self):
        client_mock = MagicMock()
        client_mock.getCandleData.return_value = {"status": False, "message": "No data"}

        with patch("app.history.client.AngelClient.login", return_value=client_mock):
            candles = HistoryClient.get_candles(
                exchange="NSE",
                symbol_token="26000",
                interval="ONE_MINUTE",
                from_date=datetime(2024, 1, 1, 0, 0),
                to_date=datetime(2024, 1, 1, 0, 5),
            )

        assert candles == []

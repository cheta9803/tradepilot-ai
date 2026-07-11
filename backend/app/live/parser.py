from datetime import datetime
from zoneinfo import ZoneInfo

from app.instruments.models import Instrument


class LiveParser:

    @staticmethod
    def parse(
        message: dict,
        instrument: Instrument,
    ) -> dict:

        exchange_timestamp = message.get("exchange_timestamp")

        if exchange_timestamp:

            timestamp = datetime.now(
                ZoneInfo("Asia/Kolkata"),
            )

        else:

            timestamp = datetime.now(
                ZoneInfo("Asia/Kolkata"),
            )

        return {
            "exchange": instrument.exchange,
            "symbol": instrument.symbol,
            "trading_symbol": instrument.trading_symbol,
            "token": instrument.token,
            "ltp": message.get("last_traded_price", 0) / 100,
            "open": message.get("open_price_of_the_day", 0) / 100,
            "high": message.get("high_price_of_the_day", 0) / 100,
            "low": message.get("low_price_of_the_day", 0) / 100,
            "close": message.get("closed_price", 0) / 100,
            "volume": message.get("volume_trade_for_the_day", 0),
            "timestamp": timestamp,
        }
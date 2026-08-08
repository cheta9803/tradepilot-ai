from datetime import datetime
from zoneinfo import ZoneInfo

from app.instruments.models import Instrument


class LiveParser:

    IST = ZoneInfo("Asia/Kolkata")

    _day_volume: dict[str, int] = {}

    @classmethod
    def parse(
        cls,
        message: dict,
        instrument: Instrument,
    ) -> dict:

        if not isinstance(message, dict):
            raise ValueError(
                "Invalid WebSocket message",
            )

        token = str(
            message.get(
                "token",
                instrument.token,
            ),
        )

        raw_ltp = message.get(
            "last_traded_price",
        )

        if raw_ltp is None:
            raise ValueError(
                "Missing last_traded_price",
            )

        ltp = float(raw_ltp) / 100

        if ltp <= 0:
            raise ValueError(
                f"Invalid LTP: {ltp}",
            )

        timestamp = cls._parse_exchange_timestamp(
            message.get(
                "exchange_timestamp",
            ),
        )

        cumulative_volume = int(
            message.get(
                "volume_trade_for_the_day",
                0,
            )
            or 0
        )

        previous_volume = cls._day_volume.get(
            token,
        )

        if previous_volume is None:

            volume = 0

        elif cumulative_volume >= previous_volume:

            volume = (
                cumulative_volume
                - previous_volume
            )

        else:
            # Broker day-volume reset.
            volume = cumulative_volume

        cls._day_volume[token] = (
            cumulative_volume
        )

        return {
            "exchange": instrument.exchange,

            "symbol": instrument.symbol,

            "trading_symbol": instrument.trading_symbol,

            "token": instrument.token,

            "ltp": ltp,

            "open": cls._price(
                message.get(
                    "open_price_of_the_day",
                    0,
                ),
            ),

            "high": cls._price(
                message.get(
                    "high_price_of_the_day",
                    0,
                ),
            ),

            "low": cls._price(
                message.get(
                    "low_price_of_the_day",
                    0,
                ),
            ),

            "close": cls._price(
                message.get(
                    "closed_price",
                    0,
                ),
            ),

            # IMPORTANT:
            # This is incremental tick volume,
            # not broker's cumulative day volume.
            "volume": volume,

            "timestamp": timestamp,
        }

    @classmethod
    def _parse_exchange_timestamp(
        cls,
        value,
    ) -> datetime:

        if value is None:
            raise ValueError(
                "Missing exchange_timestamp",
            )

        try:

            timestamp = int(value)

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                f"Invalid exchange_timestamp: {value}",
            ) from exc

        # Angel One exchange_timestamp is epoch
        # milliseconds. Support seconds as well
        # defensively.
        if timestamp > 10_000_000_000:

            timestamp /= 1000

        return datetime.fromtimestamp(
            timestamp,
            tz=cls.IST,
        )

    @staticmethod
    def _price(
        value,
    ) -> float:

        if value is None:
            return 0.0

        return float(value) / 100
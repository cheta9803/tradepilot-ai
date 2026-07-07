from app.instruments.cache import InstrumentCache
from app.live.client import LiveClient
from app.live.parser import LiveParser
from app.live.redis_cache import LiveCache


class LiveManager:

    def __init__(self):
        self.client = LiveClient()

        self.client.client.on_open = self.on_open
        self.client.client.on_data = self.on_data
        self.client.client.on_error = self.on_error
        self.client.client.on_close = self.on_close

    def start(self):
        self.client.connect()

    def stop(self):
        self.client.close()

    def subscribe(
        self,
        exchange: str,
        token: str,
    ):
        exchange_map = {
            "NSE": 1,
            "BSE": 3,
        }

        exchange_type = exchange_map.get(exchange.upper())

        print(
            f"Subscribing: exchange={exchange}, "
            f"exchangeType={exchange_type}, token={token}"
        )

        self.client.client.subscribe(
            correlation_id="tradepilot",
            mode=1,
            token_list=[
                {
                    "exchangeType": exchange_type,
                    "tokens": [token],
                }
            ],
        )

        print("Subscribe request sent.")

    def unsubscribe(
        self,
        exchange: str,
        token: str,
    ):
        self.client.client.unsubscribe(
            correlation_id="tradepilot",
            mode=1,
            token_list=[
                {
                    "exchangeType": exchange,
                    "tokens": [token],
                }
            ],
        )

    def on_open(self, ws):
        print("Live WebSocket Connected")

    def on_close(self, ws):
        print("Live WebSocket Closed")

    def on_error(self, ws, error):
        print(error)

    def on_data(
        self,
        ws,
        message,
    ):
        print("=" * 80)
        print("LIVE MESSAGE RECEIVED")
        print(message)
        print("=" * 80)

        token = str(message.get("token"))

        instrument = InstrumentCache.get_by_token(token)

        if instrument is None:
            print(f"Instrument not found for token {token}")
            return

        data = LiveParser.parse(
            message=message,
            instrument=instrument,
        )

        LiveCache.save(
            token,
            data,
        )

        print(f"Saved {instrument.symbol} to Redis.")
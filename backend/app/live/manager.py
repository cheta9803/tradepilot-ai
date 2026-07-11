from app.instruments.cache import InstrumentCache
from app.live.client import LiveClient
from app.live.parser import LiveParser
from app.live.redis_cache import LiveCache
from app.watchlist.startup import WatchlistStartup
from app.candles.service import CandleService


class LiveManager:

    def __init__(self):
        self.client = LiveClient()

        self.client.client.on_open = self.on_open
        self.client.client.on_data = self.on_data
        self.client.client.on_error = self.on_error
        self.client.client.on_close = self.on_close

        self.subscribed_tokens: set[str] = set()

    def start(self):
        self.client.connect()

    def stop(self):
        self.client.close()

    def subscribe(
        self,
        exchange: str,
        token: str,
    ):

        if token in self.subscribed_tokens:
            print(f"{token} already subscribed.")
            return

        exchange_type = (
            1 if exchange == "NSE"
            else 3
        )

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

        self.subscribed_tokens.add(token)

        print("Subscribe request sent.")

    def unsubscribe(
        self,
        exchange: str,
        token: str,
    ):

        if token not in self.subscribed_tokens:
            print(f"{token} is not subscribed.")
            return

        exchange_type = (
            1 if exchange == "NSE"
            else 3
        )

        print(
            f"Unsubscribing: exchange={exchange}, "
            f"exchangeType={exchange_type}, token={token}"
        )

        self.client.client.unsubscribe(
            correlation_id="tradepilot",
            mode=1,
            token_list=[
                {
                    "exchangeType": exchange_type,
                    "tokens": [token],
                }
            ],
        )

        self.subscribed_tokens.remove(token)

        print("Unsubscribe request sent.")

    def on_open(self, ws):
        print("Live WebSocket Connected")

        WatchlistStartup.subscribe_all()

    def on_close(self, ws):
        print("Live WebSocket Closed")

    def on_error(self, ws, error):
        print(error)

    def on_data(
        self,
        ws,
        message,
    ):
        print("\n" + "=" * 80)
        print("LIVE TICK RECEIVED")
        print(message)
        print("=" * 80)

        token = str(message.get("token"))

        print(f"Token: {token}")

        instrument = InstrumentCache.get_by_token(token)

        print(f"Instrument Found: {instrument is not None}")

        if instrument is None:
            print("Instrument not found in cache.")
            return

        data = LiveParser.parse(
            message=message,
            instrument=instrument,
        )

        print(f"LTP: {data['ltp']}")
        print(f"Volume: {data['volume']}")

        try:
            LiveCache.save(
                token,
                data,
            )
            print("LiveCache saved.")
        except Exception:
            import traceback
            print("LiveCache Exception")
            traceback.print_exc()

        try:
            CandleService.process_tick(
                exchange=instrument.exchange,
                symbol=instrument.symbol,
                token=instrument.token,
                price=data["ltp"],
                volume=data["volume"],
                timestamp=data["timestamp"],
            )

            print("CandleService completed successfully.")

        except Exception as e:
            import traceback

            print("\n" + "=" * 80)
            print("CandleService Exception")
            traceback.print_exc()
            print("=" * 80)
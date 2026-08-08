from app.candles.service import CandleService
from app.core.logger import logger
from app.instruments.cache import InstrumentCache
from app.live.client import LiveClient
from app.live.parser import LiveParser
from app.live.redis_cache import LiveCache
from app.market.service import market_service
from app.trades.monitor import TradeMonitor
from app.watchlist.startup import WatchlistStartup
from app.websocket.manager import websocket_manager


class LiveManager:

    def __init__(self):

        self.client = LiveClient()
        self.subscribed_tokens: set[str] = set()

    def _attach_callbacks(self) -> None:

        if self.client.client is None:
            return

        self.client.client.on_open = self.on_open
        self.client.client.on_data = self.on_data
        self.client.client.on_error = self.on_error
        self.client.client.on_close = self.on_close

    def start(self):

        logger.info(
            "Starting Live WebSocket...",
        )

        try:
            self.client.initialize()
        except Exception as exc:
            logger.warning("Live client initialization failed: %s", exc)
            return

        self._attach_callbacks()

        try:
            self.client.connect()
        except Exception as exc:
            logger.warning("Live client connection failed: %s", exc)

    def stop(self):

        logger.info(
            "Stopping Live WebSocket...",
        )

        self.client.close()

    def subscribe(
        self,
        exchange: str,
        token: str,
    ):

        if token in self.subscribed_tokens:

            logger.debug(
                "%s already subscribed.",
                token,
            )

            return

        exchange_type = (
            1
            if exchange == "NSE"
            else 3
        )

        logger.info(
            "Subscribing: exchange=%s exchangeType=%s token=%s",
            exchange,
            exchange_type,
            token,
        )

        self.client.client.subscribe(
            correlation_id="tradepilot",
            mode=1,
            token_list=[
                {
                    "exchangeType": exchange_type,
                    "tokens": [
                        token,
                    ],
                },
            ],
        )

        self.subscribed_tokens.add(
            token,
        )

        logger.info(
            "Subscription request sent for %s.",
            token,
        )

    def unsubscribe(
        self,
        exchange: str,
        token: str,
    ):

        if token not in self.subscribed_tokens:

            logger.debug(
                "%s is not subscribed.",
                token,
            )

            return

        exchange_type = (
            1
            if exchange == "NSE"
            else 3
        )

        logger.info(
            "Unsubscribing: exchange=%s exchangeType=%s token=%s",
            exchange,
            exchange_type,
            token,
        )

        self.client.client.unsubscribe(
            correlation_id="tradepilot",
            mode=1,
            token_list=[
                {
                    "exchangeType": exchange_type,
                    "tokens": [
                        token,
                    ],
                },
            ],
        )

        self.subscribed_tokens.remove(
            token,
        )

        logger.info(
            "Unsubscribe request sent for %s.",
            token,
        )

    def on_open(
        self,
        ws,
    ):

        logger.info(
            "Live WebSocket Connected",
        )

        self.client.mark_connected()

        WatchlistStartup.subscribe_all()

    def on_close(
        self,
        ws,
    ):

        logger.warning(
            "Live WebSocket Closed",
        )

        self.client.mark_disconnected()

    def on_error(
        self,
        ws,
        error,
    ):

        logger.exception(
            "Live WebSocket Error: %s",
            error,
        )

    def on_data(
        self,
        ws,
        message,
    ):

        try:

            logger.debug(
                "Tick received: %s",
                message,
            )

            token = str(
                message.get(
                    "token",
                ),
            )

            instrument = InstrumentCache.get_by_token(
                token,
            )

            if instrument is None:

                logger.warning(
                    "Unknown instrument token received: %s",
                    token,
                )

                return

            data = LiveParser.parse(
                message=message,
                instrument=instrument,
            )

            LiveCache.save(
                token,
                data,
            )

            market_service.update_tick(
                data,
            )

            broadcast_data = {
                **data,
                "timestamp": data["timestamp"].isoformat(),
            }

            websocket_manager.broadcast_threadsafe(
                broadcast_data,
            )

            CandleService.process_tick(
                exchange=instrument.exchange,
                symbol=instrument.symbol,
                token=instrument.token,
                price=data["ltp"],
                volume=data["volume"],
                timestamp=data["timestamp"],
            )

            for timeframe in (
                "1m",
                "5m",
            ):

                TradeMonitor.update(
                    exchange=instrument.exchange,
                    token=instrument.token,
                    timeframe=timeframe,
                )

        except Exception:

            logger.exception(
                "Unhandled exception while processing live tick.",
            )
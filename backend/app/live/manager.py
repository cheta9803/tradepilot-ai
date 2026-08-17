import threading

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
        self._subscribed_generation: int | None = None
        self._subscription_lock = threading.Lock()
        self._history_thread: threading.Thread | None = None
        self._history_lock = threading.Lock()

    def _attach_callbacks(self) -> None:
        self.client.set_callbacks(
            on_open=self.on_open,
            on_data=self.on_data,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def start(self):
        logger.info("Starting Live WebSocket...")
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
        logger.info("Stopping Live WebSocket...")
        self.client.close()
        self._clear_subscription_state()

    def _clear_subscription_state(self) -> None:
        with self._subscription_lock:
            self.subscribed_tokens.clear()
            self._subscribed_generation = None

    def _prepare_subscription_generation(self) -> int:
        health = self.client.health()
        generation = int(health["connection_generation"])

        with self._subscription_lock:
            if self._subscribed_generation != generation:
                previous_count = len(self.subscribed_tokens)
                self.subscribed_tokens.clear()
                self._subscribed_generation = generation

                if previous_count:
                    logger.info(
                        "Resetting live subscription state for new WebSocket "
                        "generation=%s (previous_count=%s).",
                        generation,
                        previous_count,
                    )

        return generation

    def health(self) -> dict:
        health = self.client.health()
        generation = int(health["connection_generation"])

        with self._subscription_lock:
            subscribed_tokens = (
                sorted(self.subscribed_tokens)
                if self._subscribed_generation == generation
                else []
            )

        health.update({
            "subscribed_tokens": len(subscribed_tokens),
            "subscribed_token_list": subscribed_tokens,
        })
        return health

    def subscribe(self, exchange: str, token: str):
        client = self.client.client
        if client is None:
            logger.warning(
                "Cannot subscribe: Live WebSocket client is not initialized."
            )
            return

        generation = self._prepare_subscription_generation()

        with self._subscription_lock:
            if token in self.subscribed_tokens:
                logger.debug(
                    "%s already subscribed for WebSocket generation=%s.",
                    token,
                    generation,
                )
                return

        exchange_type = 1 if exchange == "NSE" else 3
        logger.info(
            "Subscribing: exchange=%s exchangeType=%s token=%s generation=%s",
            exchange,
            exchange_type,
            token,
            generation,
        )

        client.subscribe(
            correlation_id="tradepilot",
            mode=1,
            token_list=[
                {
                    "exchangeType": exchange_type,
                    "tokens": [token],
                }
            ],
        )

        with self._subscription_lock:
            # The socket may theoretically change while the broker call is in
            # flight. Only record the token for the generation that sent it.
            current_generation = int(
                self.client.health()["connection_generation"]
            )
            if current_generation == generation:
                self.subscribed_tokens.add(token)
                self._subscribed_generation = generation

        logger.info(
            "Subscription request sent for %s generation=%s.",
            token,
            generation,
        )

    def unsubscribe(self, exchange: str, token: str):
        client = self.client.client
        if client is None:
            return

        generation = self._prepare_subscription_generation()

        with self._subscription_lock:
            if token not in self.subscribed_tokens:
                return

        exchange_type = 1 if exchange == "NSE" else 3
        logger.info(
            "Unsubscribing: exchange=%s exchangeType=%s token=%s generation=%s",
            exchange,
            exchange_type,
            token,
            generation,
        )

        client.unsubscribe(
            correlation_id="tradepilot",
            mode=1,
            token_list=[
                {
                    "exchangeType": exchange_type,
                    "tokens": [token],
                }
            ],
        )

        with self._subscription_lock:
            self.subscribed_tokens.discard(token)

        logger.info("Unsubscribe request sent for %s.", token)

    def on_open(self, ws, *args, **kwargs):
        logger.info("Live WebSocket Connected")
        self.client.mark_connected()

        # This is the critical reconnect fix: every new WebSocket generation
        # starts with an empty TradePilot subscription set. The broker socket
        # itself is also fresh, so all required instruments must be sent again.
        generation = self._prepare_subscription_generation()
        logger.info(
            "Live WebSocket generation=%s is ready for fresh subscriptions.",
            generation,
        )

        health = self.client.health()
        logger.info(
            "Live feed health: state=%s generation=%s",
            health["state"],
            health["connection_generation"],
        )

        try:
            WatchlistStartup.subscribe_all(load_history=False)
            logger.info(
                "Live market subscriptions initialized: generation=%s tokens=%s.",
                generation,
                len(self.subscribed_tokens),
            )
        except Exception as exc:
            logger.exception(
                "Live market subscription initialization failed: %s",
                exc,
            )

        self._start_history_background()

    def _start_history_background(self) -> None:
        with self._history_lock:
            if self._history_thread is not None and self._history_thread.is_alive():
                logger.info("Historical warm-up is already running.")
                return
            self._history_thread = threading.Thread(
                target=self._load_history_background,
                name="HistoryWarmup",
                daemon=True,
            )
            self._history_thread.start()
        logger.info("Historical warm-up started in background.")

    def _load_history_background(self) -> None:
        try:
            WatchlistStartup.load_history()
            logger.info("Historical warm-up background task completed.")
        except Exception as exc:
            logger.exception("Historical warm-up background task failed: %s", exc)

    def on_close(self, ws, close_status_code=None, close_msg=None, *args, **kwargs):
        logger.warning(
            "Live WebSocket Closed: code=%s message=%s",
            close_status_code,
            close_msg,
        )
        self.client.mark_disconnected()
        self._clear_subscription_state()
        logger.warning("Live feed disconnected. Health=%s", self.client.health())

    def on_error(self, ws, error, *args, **kwargs):
        error_text = str(error)
        logger.error("Live WebSocket Error: %s", error_text)

        # SmartWebSocketV2 can report "Connection closed" through on_error
        # without giving us a useful subscription reset through on_close.
        # Clear only for a connection-level error; ordinary protocol errors
        # should not make a healthy socket appear unsubscribed.
        if "connection closed" in error_text.lower():
            self._clear_subscription_state()

    def on_data(self, ws, message, *args, **kwargs):
        try:
            if not isinstance(message, dict):
                logger.debug("Ignoring non-dict WebSocket message: %r", message)
                return
            token = message.get("token")
            if token is None:
                logger.debug("Ignoring WebSocket message without token: %s", message)
                return
            raw_ltp = message.get("last_traded_price")
            if raw_ltp is None:
                logger.debug("Ignoring WebSocket message without LTP: %s", message)
                return
            instrument = InstrumentCache.get_by_token(str(token))
            if instrument is None:
                logger.warning("Unknown instrument token received: %s", token)
                return
            data = LiveParser.parse(message=message, instrument=instrument)
            LiveCache.save(str(token), data)
            market_service.update_tick(data)
            broadcast_data = {**data, "timestamp": data["timestamp"].isoformat()}
            websocket_manager.broadcast_threadsafe(broadcast_data)
            CandleService.process_tick(
                exchange=instrument.exchange,
                symbol=instrument.symbol,
                token=instrument.token,
                price=data["ltp"],
                volume=data["volume"],
                timestamp=data["timestamp"],
            )
            for timeframe in ("1m", "5m"):
                TradeMonitor.update(
                    exchange=instrument.exchange,
                    token=instrument.token,
                    timeframe=timeframe,
                )
        except ValueError as exc:
            logger.warning("Ignoring invalid live tick: %s", exc)
        except Exception:
            logger.exception("Unhandled exception while processing live tick.")

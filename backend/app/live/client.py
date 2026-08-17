import threading
import time
from datetime import datetime, time as dt_time
from enum import Enum
from typing import Callable
from zoneinfo import ZoneInfo

from SmartApi.smartWebSocketV2 import SmartWebSocketV2

from app.angel.client import AngelClient
from app.core.config import settings
from app.core.logger import logger


class ConnectionState(Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"


class LiveClient:
    """Own the Angel market-data connection and reconnect lifecycle.

    TradePilot owns the reconnect/backoff lifecycle. SmartWebSocketV2 owns
    the websocket protocol and heartbeat implementation.

    A new SmartWebSocketV2 instance represents a new connection generation.
    Tick/pong timestamps are reset for every generation so health information
    from an old socket can never make a new socket look healthy or stale.
    """

    MARKET_TIMEZONE = ZoneInfo("Asia/Kolkata")
    MARKET_OPEN = dt_time(9, 15)
    MARKET_CLOSE = dt_time(15, 30)

    def __init__(self):
        self.smart_api = None
        self.feed_token = None
        self.client = None

        self.state = ConnectionState.DISCONNECTED
        self._thread: threading.Thread | None = None
        self._watchdog_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._state_lock = threading.Lock()
        self._client_lock = threading.Lock()

        self._on_open: Callable | None = None
        self._on_data: Callable | None = None
        self._on_error: Callable | None = None
        self._on_close: Callable | None = None

        self.reconnect_attempts = 0
        self.last_connected_at: float | None = None
        self.last_disconnected_at: float | None = None
        self.last_tick_at: float | None = None
        self.last_pong_at: float | None = None
        self.last_error: str | None = None

        # Every newly-created SmartWebSocketV2 gets a generation.
        # Callback checks compare the owner SmartWebSocketV2 object, not the
        # websocket-client WebSocketApp passed to callbacks.
        self._generation = 0

        # A newly connected socket gets a short grace period to receive its
        # first market tick. This prevents an immediate false reconnect while
        # subscriptions are being restored.
        self._tick_grace_until: float | None = None

    def set_callbacks(
        self,
        *,
        on_open: Callable,
        on_data: Callable,
        on_error: Callable,
        on_close: Callable,
    ) -> None:
        self._on_open = on_open
        self._on_data = on_data
        self._on_error = on_error
        self._on_close = on_close

        with self._client_lock:
            client = self.client
            generation = self._generation

        if client is not None:
            self._attach_callbacks(client, generation)

    def initialize(self):
        with self._client_lock:
            if self.client is not None:
                return
            self._build_client_locked()

    def _build_client(self):
        with self._client_lock:
            self._build_client_locked()

    def _build_client_locked(self):
        smart_api = AngelClient.get_client()
        feed_token = smart_api.getfeedToken()

        # SmartWebSocketV2 keeps subscription state on class attributes.
        # TradePilot owns reconnects, so every new socket must start with a
        # clean SDK subscription state.
        SmartWebSocketV2.RESUBSCRIBE_FLAG = False
        SmartWebSocketV2.input_request_dict = {}

        client = SmartWebSocketV2(
            auth_token=getattr(smart_api, "access_token", None),
            api_key=settings.angel_api_key,
            client_code=settings.angel_client_id,
            feed_token=feed_token,
            # LiveClient owns reconnect/backoff.
            max_retry_attempt=0,
            retry_strategy=0,
            retry_delay=10,
            retry_duration=60,
        )

        self._generation += 1
        generation = self._generation

        self.smart_api = smart_api
        self.feed_token = feed_token
        self.client = client

        self._attach_callbacks(client, generation)

    def _is_current_client(self, owner, generation: int) -> bool:
        with self._client_lock:
            return owner is self.client and generation == self._generation

    def _attach_callbacks(self, client, generation: int) -> None:
        owner = client

        def on_open(ws, *args, **kwargs):
            if not self._is_current_client(owner, generation):
                logger.debug(
                    "Ignoring on_open from stale Angel WebSocket generation=%d.",
                    generation,
                )
                return

            if callable(self._on_open):
                self._on_open(ws)

        def on_data(ws, message, *args, **kwargs):
            if not self._is_current_client(owner, generation):
                logger.debug(
                    "Ignoring on_data from stale Angel WebSocket generation=%d.",
                    generation,
                )
                return

            self.mark_tick()

            if callable(self._on_data):
                self._on_data(ws, message)

        def on_error(ws, error, *args, **kwargs):
            if not self._is_current_client(owner, generation):
                logger.debug(
                    "Ignoring on_error from stale Angel WebSocket generation=%d.",
                    generation,
                )
                return

            self.last_error = str(error)

            if callable(self._on_error):
                self._on_error(ws, error)

        def on_close(ws, *args, **kwargs):
            if not self._is_current_client(owner, generation):
                logger.debug(
                    "Ignoring on_close from stale Angel WebSocket generation=%d.",
                    generation,
                )
                return

            self.mark_disconnected()

            if callable(self._on_close):
                self._on_close(ws, *args, **kwargs)

        client.on_open = on_open
        client.on_data = on_data
        client.on_error = on_error
        client.on_close = on_close

        # Compatibility fix for the installed websocket-client version.
        # websocket-client invokes its on_close callback as
        #   on_close(wsapp, close_status_code, close_msg)
        # while the current SmartWebSocketV2 SDK defines _on_close(self, wsapp)
        # and therefore raises:
        #   SmartWebSocketV2._on_close() takes 2 positional arguments but 4 were given
        #
        # SmartWebSocketV2.connect() passes self._on_close directly to
        # websocket.WebSocketApp, so overriding only client.on_close is not
        # enough. Adapt the SDK's internal callback to accept the newer
        # websocket-client callback signature and forward it to our
        # generation-safe callback above.
        def sdk_on_close(wsapp, *args, **kwargs):
            client.on_close(wsapp, *args, **kwargs)

        client._on_close = sdk_on_close

        # Do not replace SmartWebSocketV2.on_pong. The SDK's internal
        # _on_pong() updates client.last_pong_timestamp.

    def connect(self):
        with self._state_lock:
            if self._thread is not None and self._thread.is_alive():
                return

        self._stop_event.clear()
        self._set_state(ConnectionState.CONNECTING)

        thread = threading.Thread(
            target=self._run_supervisor,
            name="AngelLiveSupervisor",
            daemon=True,
        )

        with self._state_lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._thread = thread

        thread.start()

        if (
            self._watchdog_thread is None
            or not self._watchdog_thread.is_alive()
        ):
            self._watchdog_thread = threading.Thread(
                target=self._run_watchdog,
                name="AngelLiveWatchdog",
                daemon=True,
            )
            self._watchdog_thread.start()

    def _run_supervisor(self):
        delay = max(1, settings.live_ws_reconnect_initial_seconds)
        max_delay = max(delay, settings.live_ws_reconnect_max_seconds)

        while not self._stop_event.is_set():
            try:
                with self._client_lock:
                    self._build_client_locked()
                    client = self.client

                self._set_state(ConnectionState.CONNECTING)

                logger.info(
                    "Connecting Angel market WebSocket (attempt=%d).",
                    self.reconnect_attempts + 1,
                )

                client.connect()

                if self._stop_event.is_set():
                    break

                self.reconnect_attempts += 1
                self._set_state(ConnectionState.DISCONNECTED)

                logger.warning(
                    "Angel market WebSocket connect() returned; "
                    "reconnecting in %ss.",
                    delay,
                )

            except Exception as exc:
                if self._stop_event.is_set():
                    break

                self.reconnect_attempts += 1
                self.last_error = str(exc)
                self._set_state(ConnectionState.DISCONNECTED)

                logger.exception(
                    "Angel market WebSocket supervisor failure; "
                    "reconnecting in %ss.",
                    delay,
                )

            if self._stop_event.wait(delay):
                break

            delay = min(max_delay, max(delay * 2, 1))

        self._set_state(ConnectionState.DISCONNECTED)

    @classmethod
    def _is_nse_market_hours(cls) -> bool:
        now = datetime.now(cls.MARKET_TIMEZONE)

        # Monday-Friday only. This deliberately excludes weekends.
        if now.weekday() >= 5:
            return False

        return cls.MARKET_OPEN <= now.time() <= cls.MARKET_CLOSE

    def _run_watchdog(self):
        """Detect a stale live feed during NSE market hours.

        Outside market hours, lack of ticks is normal and is ignored.

        During market hours, the watchdog checks both heartbeat and market
        ticks. A new connection gets a grace period for its first tick so the
        socket can finish subscription restoration before being judged stale.
        """

        timeout = max(60, settings.live_ws_heartbeat_timeout_seconds)

        while not self._stop_event.wait(5):
            if self.state != ConnectionState.CONNECTED:
                continue

            if not self._is_nse_market_hours():
                continue

            with self._client_lock:
                client = self.client
                generation = self._generation

            if client is None:
                continue

            now = time.time()

            # Only accept the SDK timestamp when it belongs to the current
            # connection. This prevents a stale SDK timestamp from a previous
            # socket from making the new socket appear unhealthy immediately.
            sdk_pong = getattr(client, "last_pong_timestamp", None)
            if (
                sdk_pong is not None
                and self.last_connected_at is not None
                and sdk_pong >= self.last_connected_at
            ):
                self.last_pong_at = sdk_pong

            pong_age = (
                None
                if self.last_pong_at is None
                else now - self.last_pong_at
            )

            tick_age = (
                None
                if self.last_tick_at is None
                else now - self.last_tick_at
            )

            # IMPORTANT: do not force a reconnect from pong age alone.
            # SmartWebSocketV2 owns the websocket-client heartbeat and its
            # internal pong timestamp depends on the broker heartbeat payload.
            # In practice that timestamp can remain stale even while market
            # ticks are arriving normally. Treating pong age as a hard failure
            # therefore creates a false reconnect loop (observed roughly every
            # 60 seconds). During market hours, the market-data tick stream is
            # the authoritative feed-health signal.
            no_tick_after_grace = (
                self.last_tick_at is None
                and self._tick_grace_until is not None
                and now >= self._tick_grace_until
            )

            stale_ticks = (
                no_tick_after_grace
                or (
                    self.last_tick_at is not None
                    and tick_age is not None
                    and tick_age > timeout
                )
            )

            if not stale_ticks:
                # Pong age is retained in health() for diagnostics, but a
                # stale SDK pong must not tear down a socket that is receiving
                # fresh market ticks.
                continue

            logger.warning(
                "Angel live feed stale during market hours: "
                "generation=%s pong_age=%s tick_age=%s; forcing reconnect.",
                generation,
                None if pong_age is None else round(pong_age, 1),
                None if tick_age is None else round(tick_age, 1),
            )

            self.last_error = (
                "Live feed stale during market hours "
                f"(generation={generation}, "
                f"pong_age={None if pong_age is None else round(pong_age, 1)}, "
                f"tick_age={None if tick_age is None else round(tick_age, 1)})"
            )

            try:
                client.close_connection()
            except Exception:
                logger.exception("Failed to close stale Angel WebSocket.")

    def mark_connected(self):
        now = time.time()
        timeout = max(60, settings.live_ws_heartbeat_timeout_seconds)

        self.last_connected_at = now
        self.last_disconnected_at = None

        # IMPORTANT: these belong to the new connection generation. Never
        # carry a tick timestamp from the old socket into the new socket.
        self.last_tick_at = None
        self.last_pong_at = now
        self._tick_grace_until = now + timeout
        self.last_error = None
        self._set_state(ConnectionState.CONNECTED)

    def mark_disconnected(self):
        self.last_disconnected_at = time.time()
        self._set_state(ConnectionState.DISCONNECTED)

    def mark_tick(self):
        self.last_tick_at = time.time()

    def mark_pong(self):
        # Retained for compatibility with existing callers/tests.
        self.last_pong_at = time.time()

    def _set_state(self, state: ConnectionState):
        with self._state_lock:
            self.state = state

    def health(self) -> dict:
        now = time.time()

        def age(value):
            if value is None:
                return None
            return round(max(0.0, now - value), 1)

        with self._client_lock:
            generation = self._generation
            client = self.client

        sdk_pong = getattr(client, "last_pong_timestamp", None)
        if (
            sdk_pong is not None
            and self.last_connected_at is not None
            and sdk_pong >= self.last_connected_at
        ):
            self.last_pong_at = sdk_pong

        return {
            "state": self.state.value,
            "reconnect_attempts": self.reconnect_attempts,
            "connection_generation": generation,
            "client_exists": client is not None,
            "last_connected_at": self.last_connected_at,
            "last_disconnected_at": self.last_disconnected_at,
            "last_tick_age_seconds": age(self.last_tick_at),
            "last_pong_age_seconds": age(self.last_pong_at),
            "last_error": self.last_error,
        }

    def close(self):
        self._stop_event.set()
        self.mark_disconnected()

        with self._client_lock:
            client = self.client
            self._generation += 1

        if client is not None:
            try:
                client.close_connection()
            except Exception:
                logger.exception("Failed to close Angel market WebSocket.")

        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2)

        with self._state_lock:
            self._thread = None

        with self._client_lock:
            self.client = None
            self.smart_api = None
            self.feed_token = None

        self.last_tick_at = None
        self.last_pong_at = None
        self._tick_grace_until = None

        watchdog = self._watchdog_thread
        if (
            watchdog is not None
            and watchdog is not threading.current_thread()
        ):
            watchdog.join(timeout=2)

        self._watchdog_thread = None
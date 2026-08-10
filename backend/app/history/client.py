from threading import Lock
from time import monotonic, sleep

from app.angel.client import AngelClient
from app.core.logger import logger


class HistoryClient:

    _lock = Lock()

    # Keep historical API traffic deliberately conservative.
    #
    # Angel documents getCandleData at 3 requests/second and
    # 180 requests/minute. We intentionally use 1 request/second
    # to avoid bursts while loading the Nifty universe.
    MIN_INTERVAL_SECONDS = 1.0

    # If Angel returns AB1021, stop making historical requests
    # for a while instead of immediately retrying.
    RATE_LIMIT_COOLDOWN_SECONDS = 30.0

    _last_request_at = 0.0
    _rate_limited_until = 0.0

    @classmethod
    def _wait_for_rate_limit(cls) -> None:
        with cls._lock:

            now = monotonic()

            next_allowed_at = max(
                cls._last_request_at
                + cls.MIN_INTERVAL_SECONDS,
                cls._rate_limited_until,
            )

            wait = next_allowed_at - now

            if wait > 0:
                logger.debug(
                    "Historical API throttling: waiting %.2f seconds.",
                    wait,
                )

                sleep(wait)

            cls._last_request_at = monotonic()

    @staticmethod
    def _is_rate_limit_error(
        exc: Exception,
    ) -> bool:

        message = str(exc).lower()

        return (
            "too many requests" in message
            or "exceeding access rate" in message
            or "access rate" in message
            or "ab1021" in message
        )

    @classmethod
    def get_candles(
        cls,
        *,
        exchange: str,
        symbol_token: str,
        interval: str,
        from_date,
        to_date,
    ) -> list[dict]:

        try:

            cls._wait_for_rate_limit()

            client = AngelClient.login()

            response = client.getCandleData(
                {
                    "exchange": exchange,
                    "symboltoken": symbol_token,
                    "interval": interval,
                    "fromdate": from_date.strftime(
                        "%Y-%m-%d %H:%M",
                    ),
                    "todate": to_date.strftime(
                        "%Y-%m-%d %H:%M",
                    ),
                }
            )

        except Exception as exc:

            if cls._is_rate_limit_error(exc):

                with cls._lock:

                    cls._rate_limited_until = (
                        monotonic()
                        + cls.RATE_LIMIT_COOLDOWN_SECONDS
                    )

                logger.warning(
                    "Angel historical API rate limit reached "
                    "for %s/%s. "
                    "Pausing historical requests for %.0f seconds.",
                    exchange,
                    symbol_token,
                    cls.RATE_LIMIT_COOLDOWN_SECONDS,
                )

                raise ValueError(
                    "Too many requests"
                ) from exc

            logger.debug(
                "Historical candle fetch failed for %s/%s: %s",
                exchange,
                symbol_token,
                exc,
            )

            return []

        if not response or not response.get("status"):

            logger.debug(
                "Historical candle fetch returned no data "
                "for %s/%s: %s",
                exchange,
                symbol_token,
                (response or {}).get(
                    "message",
                    "No data",
                ),
            )

            return []

        rows = response.get("data") or []

        logger.debug(
            "History API returned %d candles for %s/%s",
            len(rows),
            exchange,
            symbol_token,
        )

        return rows
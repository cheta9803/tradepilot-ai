from threading import Lock
from time import monotonic, sleep

from app.angel.client import AngelClient
from app.core.logger import logger


class HistoryClient:

    _lock = Lock()

    # ---------------------------------------------------------
    # Historical API throttling
    #
    # Angel historical API should not be hit aggressively.
    #
    # We intentionally stay conservative because the history
    # loader can request data for the entire Nifty universe.
    # ---------------------------------------------------------

    MIN_INTERVAL_SECONDS = 1.0

    # After Angel returns a rate-limit response, stop making
    # historical requests for this cooldown period.
    RATE_LIMIT_COOLDOWN_SECONDS = 30.0

    _last_request_at = 0.0
    _rate_limited_until = 0.0

    @classmethod
    def _wait_for_rate_limit(cls) -> None:
        """
        Wait until the next historical API request is allowed.

        Important:
        Never hold _lock while sleeping.
        """

        while True:

            with cls._lock:

                now = monotonic()

                next_allowed_at = max(
                    cls._last_request_at
                    + cls.MIN_INTERVAL_SECONDS,
                    cls._rate_limited_until,
                )

                wait = (
                    next_allowed_at
                    - now
                )

                if wait <= 0:

                    # Reserve this request slot.
                    cls._last_request_at = monotonic()

                    return

            logger.debug(
                "Historical API throttling: "
                "waiting %.2f seconds.",
                wait,
            )

            sleep(wait)

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
    def _set_rate_limit_cooldown(cls) -> None:
        """
        Globally pause historical requests after Angel
        reports a rate-limit violation.
        """

        with cls._lock:

            cls._rate_limited_until = (
                monotonic()
                + cls.RATE_LIMIT_COOLDOWN_SECONDS
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

        # -----------------------------------------------------
        # Wait before every request.
        # -----------------------------------------------------

        cls._wait_for_rate_limit()

        try:

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

                cls._set_rate_limit_cooldown()

                logger.warning(
                    "Angel historical API rate limit "
                    "reached for %s/%s. "
                    "Pausing historical requests "
                    "for %.0f seconds.",
                    exchange,
                    symbol_token,
                    cls.RATE_LIMIT_COOLDOWN_SECONDS,
                )

                raise ValueError(
                    "Too many requests"
                ) from exc

            logger.debug(
                "Historical candle fetch failed "
                "for %s/%s: %s",
                exchange,
                symbol_token,
                exc,
            )

            return []

        # -----------------------------------------------------
        # Validate broker response.
        # -----------------------------------------------------

        if (
            not response
            or not response.get("status")
        ):

            logger.debug(
                "Historical candle fetch returned "
                "no data for %s/%s: %s",
                exchange,
                symbol_token,
                (response or {}).get(
                    "message",
                    "No data",
                ),
            )

            return []

        rows = (
            response.get("data")
            or []
        )

        logger.debug(
            "History API returned %d candles "
            "for %s/%s",
            len(rows),
            exchange,
            symbol_token,
        )

        return rows
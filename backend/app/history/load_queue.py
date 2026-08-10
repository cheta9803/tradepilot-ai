from time import sleep

from app.core.logger import logger
from app.history.loader import HistoryLoader


class HistoryLoadQueue:

    # HistoryClient already enforces the minimum request interval.
    # Keep a small queue delay as an additional safety margin.
    DELAY_SECONDS = 0.25

    # Do not aggressively retry a rate-limited request.
    MAX_RETRIES = 2

    # Angel historical API cooldown is handled centrally by
    # HistoryClient. This delay is only used between retries.
    RETRY_DELAY_SECONDS = 30.0

    @classmethod
    def load(
        cls,
        instruments: list[tuple[str, str]],
    ) -> None:

        total = len(instruments)

        logger.info(
            "Starting historical load queue for %d instruments.",
            total,
        )

        for index, (exchange, token) in enumerate(
            instruments,
            start=1,
        ):

            logger.info(
                "Historical load %d/%d: %s:%s",
                index,
                total,
                exchange,
                token,
            )

            loaded = False

            for attempt in range(
                1,
                cls.MAX_RETRIES + 1,
            ):

                try:

                    HistoryLoader.load(
                        exchange=exchange,
                        token=token,
                    )

                    loaded = True
                    break

                except ValueError as ex:

                    if "Too many requests" not in str(ex):

                        logger.debug(
                            "Failed to load history "
                            "for %s:%s: %s",
                            exchange,
                            token,
                            ex,
                        )

                        break

                    logger.warning(
                        "Angel historical rate limit for "
                        "%s:%s "
                        "(attempt %d/%d). "
                        "Waiting %.0f seconds before retry.",
                        exchange,
                        token,
                        attempt,
                        cls.MAX_RETRIES,
                        cls.RETRY_DELAY_SECONDS,
                    )

                    if attempt < cls.MAX_RETRIES:

                        sleep(
                            cls.RETRY_DELAY_SECONDS
                        )

                    else:

                        logger.warning(
                            "Skipping historical load for "
                            "%s:%s after rate-limit retries.",
                            exchange,
                            token,
                        )

                except Exception as exc:

                    logger.debug(
                        "Failed to load history "
                        "for %s:%s: %s",
                        exchange,
                        token,
                        exc,
                    )

                    break

            if loaded:

                logger.debug(
                    "Historical load completed for "
                    "%s:%s.",
                    exchange,
                    token,
                )

            # Additional spacing between symbols.
            sleep(cls.DELAY_SECONDS)

        logger.info(
            "Historical load queue completed.",
        )
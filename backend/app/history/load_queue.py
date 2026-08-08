from time import sleep

from app.core.logger import logger
from app.history.loader import HistoryLoader


class HistoryLoadQueue:

    DELAY_SECONDS = 4.0

    MAX_RETRIES = 3

    RETRY_DELAY_SECONDS = 5.0

    @classmethod
    def load(
        cls,
        instruments: list[tuple[str, str]],
    ) -> None:

        for exchange, token in instruments:

            for attempt in range(1, cls.MAX_RETRIES + 1):

                try:

                    HistoryLoader.load(
                        exchange=exchange,
                        token=token,
                    )

                    break

                except ValueError as ex:

                    #
                    # Angel One rate limit
                    #
                    if "Too many requests" in str(ex):

                        logger.warning(
                            "Rate limit for %s:%s (attempt %d/%d). Retrying in %.1f sec.",
                            exchange,
                            token,
                            attempt,
                            cls.MAX_RETRIES,
                            cls.RETRY_DELAY_SECONDS,
                        )

                        if attempt < cls.MAX_RETRIES:

                            sleep(cls.RETRY_DELAY_SECONDS)

                            continue

                    logger.debug(
                        "Failed to load history for %s:%s: %s",
                        exchange,
                        token,
                        ex,
                    )

                    break

                except Exception as exc:

                    logger.debug(
                        "Failed to load history for %s:%s: %s",
                        exchange,
                        token,
                        exc,
                    )

                    break

            sleep(cls.DELAY_SECONDS)
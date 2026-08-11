from time import sleep

from app.core.logger import logger
from app.history.loader import HistoryLoader


class HistoryLoadQueue:

    # Small spacing between successful instrument requests.
    #
    # HistoryClient also applies its own request throttling,
    # so this is only an additional safety margin.
    DELAY_SECONDS = 1.0

    # Give a rate-limited instrument several opportunities.
    #
    # We deliberately keep this finite so one permanently
    # failing instrument cannot block the entire queue forever.
    MAX_RETRIES = 5

    # Wait between retries after a rate-limit response.
    #
    # HistoryClient already applies its own cooldown, so this
    # queue-level delay prevents immediately hammering the API
    # again after HistoryClient returns the rate-limit error.
    RETRY_DELAY_SECONDS = 45.0

    @classmethod
    def load(
        cls,
        instruments: list[tuple[str, str]],
    ) -> None:

        total = len(instruments)

        if total == 0:

            logger.info(
                "Historical load queue skipped: "
                "no instruments."
            )

            return

        logger.info(
            "Starting historical load queue for %d instruments.",
            total,
        )

        successful = 0
        skipped = 0

        for index, (
            exchange,
            token,
        ) in enumerate(
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

                    successful += 1

                    logger.info(
                        "Historical load completed "
                        "for %s:%s.",
                        exchange,
                        token,
                    )

                    break

                except ValueError as exc:

                    message = str(exc)

                    # ---------------------------------------------
                    # Rate limit
                    # ---------------------------------------------

                    if (
                        "Too many requests"
                        not in message
                    ):

                        logger.warning(
                            "Historical load failed "
                            "for %s:%s: %s",
                            exchange,
                            token,
                            exc,
                        )

                        break

                    logger.warning(
                        "Angel historical rate limit "
                        "for %s:%s "
                        "(attempt %d/%d). "
                        "Waiting %.0f seconds "
                        "before retry.",
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

                        continue

                    # ---------------------------------------------
                    # Retries exhausted
                    # ---------------------------------------------

                    skipped += 1

                    logger.warning(
                        "Skipping historical load for "
                        "%s:%s after %d rate-limit attempts.",
                        exchange,
                        token,
                        cls.MAX_RETRIES,
                    )

                except Exception as exc:

                    skipped += 1

                    logger.exception(
                        "Historical load failed "
                        "for %s:%s: %s",
                        exchange,
                        token,
                        exc,
                    )

                    break

            # -----------------------------------------------------
            # Spacing between instruments.
            # -----------------------------------------------------

            if index < total:

                sleep(
                    cls.DELAY_SECONDS
                )

        logger.info(
            "Historical load queue completed. "
            "Successful=%d, Skipped=%d, Total=%d.",
            successful,
            skipped,
            total,
        )
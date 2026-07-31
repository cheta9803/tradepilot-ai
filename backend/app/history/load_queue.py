from time import sleep

from app.core.logger import logger
from app.history.loader import HistoryLoader


class HistoryLoadQueue:

    DELAY_SECONDS = 0.5

    @classmethod
    def load(
        cls,
        instruments: list[tuple[str, str]],
    ) -> None:

        for exchange, token in instruments:

            try:

                HistoryLoader.load(
                    exchange=exchange,
                    token=token,
                )

            except Exception:

                logger.exception(
                    "Failed to load history for %s:%s",
                    exchange,
                    token,
                )

            sleep(cls.DELAY_SECONDS)
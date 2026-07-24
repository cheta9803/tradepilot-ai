import time
from typing import Callable, TypeVar

from app.core.domain_exceptions import RetryLimitExceededException
from app.core.logger import logger

T = TypeVar("T")


class Retry:
    DEFAULT_RETRIES = 3
    DEFAULT_DELAY = 1.0
    DEFAULT_BACKOFF = 2.0

    @classmethod
    def execute(
        cls,
        func: Callable[..., T],
        *args,
        retries: int = DEFAULT_RETRIES,
        delay: float = DEFAULT_DELAY,
        backoff: float = DEFAULT_BACKOFF,
        retry_exceptions: tuple[type[Exception], ...] = (Exception,),
        **kwargs,
    ) -> T:
        current_delay = delay
        last_exception: Exception | None = None

        for attempt in range(1, retries + 1):
            try:
                return func(*args, **kwargs)

            except retry_exceptions as e:
                last_exception = e

                logger.warning(
                    "Retry %s/%s failed: %s",
                    attempt,
                    retries,
                    e,
                )

                if attempt == retries:
                    break

                time.sleep(current_delay)
                current_delay *= backoff

        raise RetryLimitExceededException(
            f"Operation failed after {retries} attempts."
        ) from last_exception
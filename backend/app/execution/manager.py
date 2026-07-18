import threading
import time

from app.execution.engine import ExecutionEngine


class ExecutionManager:

    _running = False
    _thread = None

    @classmethod
    def start(cls) -> None:

        if cls._running:
            return

        cls._running = True

        cls._thread = threading.Thread(
            target=cls._worker,
            daemon=True,
        )

        cls._thread.start()

        print("Execution Manager Started")

    @classmethod
    def stop(cls) -> None:

        cls._running = False

        print("Execution Manager Stopped")

    @classmethod
    def _worker(cls) -> None:

        while cls._running:

            try:
                ExecutionEngine.process()

            except Exception as ex:
                print(
                    f"Execution Manager Error: {ex}"
                )

            time.sleep(1)
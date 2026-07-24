import threading
import time

from app.core.logger import logger
from app.execution.service import ExecutionService
from app.orders.sync import OrderSyncService


class ExecutionManager:

    ORDER_SYNC_INTERVAL = 5  # seconds

    def __init__(self):
        self.running = False
        self.thread: threading.Thread | None = None
        self.sync_counter = 0

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self.run,
            daemon=True,
            name="ExecutionManager",
        )

        self.thread.start()

        logger.info("Execution Manager Started")

    def stop(self):

        self.running = False

        if self.thread is not None:
            self.thread.join(timeout=5)
            self.thread = None

        logger.info("Execution Manager Stopped")

    def run(self):

        while self.running:

            try:

                # Process trading logic every second
                ExecutionService.process()

                # Synchronize broker orders every N seconds
                self.sync_counter += 1

                if (
                    self.sync_counter
                    >= self.ORDER_SYNC_INTERVAL
                ):

                    OrderSyncService.sync_all()

                    self.sync_counter = 0

            except Exception:
                logger.exception("Execution Manager Error")

            time.sleep(1)
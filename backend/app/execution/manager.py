import threading
import time

from app.execution.service import ExecutionService
from app.orders.sync import OrderSyncService


class ExecutionManager:

    ORDER_SYNC_INTERVAL = 5  # seconds

    def __init__(self):

        self.running = False
        self.thread = None
        self.sync_counter = 0

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self.run,
            daemon=True,
        )

        self.thread.start()

        print("Execution Manager Started")

    def stop(self):

        self.running = False

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

            except Exception as e:

                print(
                    f"Execution Manager Error: {e}"
                )

            time.sleep(1)
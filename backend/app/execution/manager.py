import threading
import time

from app.execution.service import ExecutionService


class ExecutionManager:

    def __init__(self):

        self.running = False
        self.thread = None

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

                ExecutionService.process()

            except Exception as e:

                print(
                    f"Execution Manager Error: {e}"
                )

            time.sleep(1)
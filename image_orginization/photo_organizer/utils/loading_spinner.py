import threading
import time


class Spinner:
    """Simple spinner for showing progress during API calls."""

    def __init__(self, message="Processing"):
        self.message = message
        self.spinner_chars = "|/-\\"
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        print("\r" + " " * (len(self.message) + 10), end="", flush=True)
        print("\r", end="", flush=True)

    def _spin(self):
        i = 0
        while self.running:
            print(
                f"\r{self.message} {self.spinner_chars[i % len(self.spinner_chars)]}",
                end="",
                flush=True,
            )
            time.sleep(0.1)
            i += 1


if __name__ == "__main__":
    spinner = Spinner("Processing")
    spinner.start()
    time.sleep(2)
    spinner.stop()
    print("Done")

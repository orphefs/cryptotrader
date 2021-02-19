import threading
import time

from src.client.restartable_thread import RestartableThread


class NormalThread(threading.Thread):

    def __init__(self, cryptotrader_thread: RestartableThread):
        super().__init__()
        self.cryptotrader_thread = cryptotrader_thread

    def run(self):
        while True:
            self.cryptotrader_thread.start()
            try:
                self.cryptotrader_thread.join()
            except Exception as e:
                print("Restarting thread due to following exception: {}".format(e))
                # For some reason this print on stdout is not visible in the main console, even though
                # when I run `sudo ifconfig enp4s0 down` the clients stop downloading data, and when I run
                # `sudo ifconfig enp4s0 up`, they resume.
                # Maybe I should just append this message to a log stream on disk.
                self.cryptotrader_thread = self.cryptotrader_thread.clone()
                time.sleep(1.0)

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
                print("Exception handled in Main,details of the exception: {}".format(e))
                self.cryptotrader_thread = self.cryptotrader_thread.clone()
                time.sleep(1.0)

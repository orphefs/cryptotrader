# Importing the modules
import os
import threading
import sys

# Custom Thread Class
import time

import websocket

from src.containers.trading_pair import TradingPair
from src.definitions import DATA_DIR
from src.run_live import run_live


class MyException(Exception):
    pass


def run_cryptotrader_instance(trading_pair: TradingPair, ws: websocket.WebSocketApp):
    try:
        print("Running cryptotrader client...")
        print("Starting " + trading_pair.as_string_for_binance() + "client")
        run_live(
            trading_pair=trading_pair,
            trade_amount=0.0,
            path_to_log=os.path.join(DATA_DIR, "live_run.log"),
            path_to_portfolio=os.path.join(DATA_DIR, "live_portfolio.dill"),
            api_key="fLKWRkS1V1yKj19G5GP4oB3m1Yuzls9GR0XK5kk0erZGwoksMULIh39vc7R47TN2",
            api_secret="Pn9czdU95eSBSoYNAtqUzZXVTloBSANBvi23w8VnvNAFTYWE9POhNs4bkXw8oFOk",
            websocket_client=ws
        )
    except Exception as e:
        return e
        # traceback.print_exc()
        # logging.info("Exited cryptotrader client: {e}".format(e))
        # time.sleep(1)
        # ws.close()
        # raise Exception("Hi, I am an exception in thread {}!".format(threading.current_thread().name))


class RestartableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs
        self.trading_pair = self._kwargs["trading_pair"]
        self.ws = self._kwargs["ws"]
        super().__init__(*args, **kwargs)

    def clone(self):
        return RestartableThread(*self._args, **self._kwargs)

    def run(self):
        self.exc = None
        try:
            run_cryptotrader_instance(self.trading_pair, self.ws)
        except BaseException as e:
            self.exc = e

    def join(self):
        threading.Thread.join(self)

        if self.exc:
            raise self.exc

    # Driver function


# def main():
#     t = MyThread()
#
#     while True:
#         t.start()
#         try:
#             t.join()
#         except Exception as e:
#             print("Exception handled in Main,details of the exception: {}".format(e))
#             t = t.clone()
#         time.sleep(1.0)

#
# # Driver code
# if __name__ == '__main__':
#     main()

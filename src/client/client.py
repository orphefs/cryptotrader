import os
import sys
import traceback

import websocket
import logging
from src.containers.trading_pair import TradingPair
from src.definitions import DATA_DIR
from src.run_live import run_live
import _thread

import threading
import time


class CryptotraderThread(threading.Thread):
    def __init__(self, trading_pair: TradingPair):
        threading.Thread.__init__(self)
        self._trading_pair = trading_pair

    def run(self):
        print("Starting " + self._trading_pair.as_string_for_binance() + "thread")
        run_cryptotrader_instance(self._trading_pair)
        print("Exiting " + self._trading_pair.as_string_for_binance() + "thread")


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    _thread.start_new_thread(run, ())


def run_cryptotrader_instance(trading_pair: TradingPair):
    try:
        print("Running cryptotrader client...")
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
        traceback.print_exc()
        logging.info("Exited cryptotrader client: {e}".format(e))
        time.sleep(1)
        ws.close()


def run(*args):
    trading_pairs = [TradingPair("XRP", "ETH"),
                     TradingPair("XRP", "BTC"),
                     TradingPair("ETH", "BTC")
                     ]
    cryptotrader_threads = []
    for trading_pair in trading_pairs:
        cryptotrader_thread = CryptotraderThread(trading_pair)
        cryptotrader_thread.start()
        cryptotrader_threads.append(cryptotrader_thread)
    # TODO: use different method to check if threads are alive and "restart" them
    # https://stackoverflow.com/questions/29692250/restarting-a-thread-in-python
    # check if threads are alive
    while True:
        for thread in cryptotrader_threads:
            if not thread.is_alive():
                thread.start()
                "Attempted to start thread: {}".format(thread.ident)
                time.sleep(1.0)
        time.sleep(1.0)
    ws.close()
    print("thread terminating...")


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:3000/",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

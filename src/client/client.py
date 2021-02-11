import os
import sys
import traceback

import websocket
import logging
from src.containers.trading_pair import TradingPair
from src.definitions import DATA_DIR
from src.run_live import run_live

try:
    import thread
except ImportError:
    import _thread as thread
import time


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    thread.start_new_thread(run, ())


def run(*args):
    try:
        print("Running cryptotrader client...")
        run_live(
            trading_pair=TradingPair("XRP", "ETH"),
            trade_amount=0.0,
            path_to_log=os.path.join(DATA_DIR, "live_run.log"),
            path_to_portfolio=os.path.join(DATA_DIR, "live_portfolio.dill"),
            api_key="fLKWRkS1V1yKj19G5GP4oB3m1Yuzls9GR0XK5kk0erZGwoksMULIh39vc7R47TN2",
            api_secret="Pn9czdU95eSBSoYNAtqUzZXVTloBSANBvi23w8VnvNAFTYWE9POhNs4bkXw8oFOk",
            websocket_client=ws
        )
    except Exception as e:
        traceback.print_exc()
        logging.info("Exited cryptotrader client: {}".format(e))
        time.sleep(1)
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

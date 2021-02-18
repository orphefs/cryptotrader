import os
import signal
import sys
import traceback

import websocket
import logging

from src.client.restartable_thread import RestartableThread
from src.client.thread import NormalThread
from src.containers.trading_pair import TradingPair
from src.definitions import DATA_DIR
from src.run_live import run_live
import _thread

import threading
import time


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    _thread.start_new_thread(run, (), {"ws": ws})


def run(*args, **kwargs):
    trading_pairs = [TradingPair("XRP", "ETH"),
                     TradingPair("XRP", "BTC"),
                     TradingPair("ETH", "BTC")
                     ]
    cryptotrader_threads = []
    for trading_pair in trading_pairs:
        cryptotrader_thread = RestartableThread(trading_pair=trading_pair, ws=kwargs["ws"])
        cryptotrader_threads.append(cryptotrader_thread)

    for cryptotrader_thread in cryptotrader_threads:
        NormalThread(cryptotrader_thread).start()


class WebSocketConnectionContextManager:
    def __init__(self, ws: websocket.WebSocketApp):
        self.ws = ws
        self.ws.on_open = on_open

    def _handle_interrupt(self):
        sys.exit()  # will trigger a exception, causing __exit__ to be called

    def __enter__(self):
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)
        self.ws.run_forever()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ws.close()


if __name__ == "__main__":
    websocket.enableTrace(True)

    with WebSocketConnectionContextManager(
            ws=websocket.WebSocketApp("ws://localhost:3000/",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close)) as ws:
        pass

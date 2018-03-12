import logging
import os
import time
from typing import List

import matplotlib

from tools.downloader import download_1_minute_data

matplotlib.use('AGG')  # generate postscript output by default
import matplotlib.pyplot as plt

from binance.client import Client

import definitions
from containers.candle import Candle
from containers.trade import Trade
from helpers import simple_moving_average
from trading_logic import get_heading, get_trend

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, '_autotrader.log'), level=logging.INFO)
is_enabled = True


def main():
    client = Client()


    while is_enabled:
        data = download_1_minute_data(client, "XRPBTC")



        time.sleep(20)


if __name__ == "__main__":
    main()

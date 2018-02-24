import logging
import os
import time
from typing import List

import matplotlib

matplotlib.use('AGG')  # generate postscript output by default
import matplotlib.pyplot as plt

from binance.client import Client

import definitions
from containers.candle import Candle
from containers.trade import Trade
from helpers import simple_moving_average
from trading_logic import get_heading, get_trend

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, '_autotrader.log'), level=logging.DEBUG)


def _plot(ax: plt.Axes, closing_prices: List[float], SMA60: List[float], EMA10: List[float]):
    """
    Plotting
    """
    """
    red    = SMA(60)
    yellow = EMA(10)
    """

    t = list(range(0, 500))
    mini = 450
    maxi = 500
    ax.clear()
    ax.plot(t[mini:maxi], closing_prices[mini:maxi], 'bo',
             t[mini:maxi], closing_prices[mini:maxi], 'g-',
             t[mini:maxi], EMA10[mini:maxi], 'y-',
             t[mini:maxi], SMA60[mini:maxi], 'r-')
    with open(os.path.join(definitions.DATA_DIR, '_candles.png'), 'bw') as out_image:
        plt.savefig(out_image)


def main():
    api_key = ""
    api_secret = ""
    client = Client(api_key, api_secret)

    closing_price_averaging_period = 60
    ps = 10
    d = 10
    buy = []
    sell = []
    prof = []
    bought = 0
    money = 0

    # Modifiable On/Off text file reading
    txt = open(definitions.CONFIG_PATH, 'r')
    is_enabled = bool(int(txt.read(1)))

    SMA = [0] * (closing_price_averaging_period - 1)
    EMA = [0] * (closing_price_averaging_period - 1)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    while is_enabled:

        # obtain candles
        candles = Candle.from_list_of_klines(client.get_klines(
            symbol='NEOUSDT', interval=Client.KLINE_INTERVAL_30MINUTE))

        trade = Trade.from_trade(client.get_recent_trades(
            symbol='NEOUSDT', limit=1)[0])

        # extract closing candle values and current value
        closing_prices = [candle.get_price().close_price for candle in candles]
        current_value = trade.price

        # Running function in order to extract long term SMA and short term EMA
        SMA60, _ = simple_moving_average(SMA, EMA, closing_price_averaging_period, closing_prices, closing_price_averaging_period)
        _, EMA10 = simple_moving_average(EMA, EMA, 10, closing_prices, closing_price_averaging_period)

        _plot(ax, closing_prices, EMA10, SMA60)

        """
        Trading Logic
        """
        """
        If the price is trending down and heading up, it is a good time to buy
        If the price is trending up and heading down, it is a good time to sell
    
        Run this code in real time in order to save profit values and eventually
        enable the buy and sell orders
        """
        trend = SMA60[499] - SMA60[498]
        head = current_value - EMA10[499]

        money = current_value

        # Decision Making
        if get_trend(trend) == "Uptrend" and get_heading(head) == "Heading Up" and not bought:
            if bought:
                logging.info('Current price is {}'.format(current_value))
                logging.info('Uptrend at {}, Heading Up at {}\n'.format(trend, head))
            elif not bought:
                logging.info('Uptrend at {}, Heading Up at {}'.format(trend, head))
                buy.append(current_value)
                bought = 1
                logging.info('bought at {}]n'.format(current_value))

        if get_trend(trend) == "Uptrend" and get_heading(head) == "Heading Down" and bought:
            if not bought:
                logging.info('Current price is {}'.format(current_value))
                logging.info('Uptrend at {}, Heading Down at {}\n'.format(trend, head))
            elif bought:
                sell.append(current_value)
                bought = 0
                logging.info('Uptrend at {}, Heading Down at {}\n'.format(trend, head))
                logging.info('sold at {}'.format(current_value))
                prof.append(sell[len(sell) - 1] - buy[len(buy) - 1] - money * current_value)
                logging.info()
                logging.info('bought at {}, sold at {}'.format(buy(len(buy) - 1)))
                logging.info('trade profit is {}, total profit is {}\n'.format(prof[len(prof)]), sum(prof))

        if get_trend(trend) == "Downtrend" and get_heading(head) == "Heading Down":
            if not bought:
                logging.info('Current price is {}'.format(current_value))
                logging.info('Downtrend at {}, Heading Down at {}\n'.format(trend, head))

            elif bought:
                logging.info('Downtrend {}, Heading Down {}\n'.format(trend, head))
                logging.info('new sell at {}'.format(current_value))
                sell.append(current_value)
                prof.append(sell[len(sell) - 1] - buy[len(buy) - 1] - money * current_value)
                bought = 0
                logging.info('bought at {}, sold at {}'.format(buy(len(buy) - 1)))
                logging.info('trade profit is {}, total profit is {}\n'.format(prof[len(prof)]), sum(prof))

        if get_trend(trend) == "Downtrend" and get_heading(head) == "Heading Up":
            if bought:
                logging.info('Current price is {}'.format(current_value))
                logging.info('Downtrend at {}, Heading Up at {}\n'.format(trend, head))

            elif not bought:
                buy.append(current_value)
                logging.info('Downtrend at {}, Heading Up {}\n'.format(trend, head))
                logging.info('new buy at {}'.format(current_value))
                bought = 1

        time.sleep(d)


if __name__ == "__main__":
    main()

from typing import Tuple

from copy import copy

from containers.candle import Candle
from plotting.plot_candles import plot_candlesticks, plot_returns
from tools.downloader import StockData, load_from_disk
import matplotlib.pyplot as plt

from type_aliases import Security


# def get_exchange_rate(security_1: Security, security_2: Security, candle: Candle) -> float:
#     candle.get_price().close_price
#     return exchange_rate

class Holdings(object):
    def __init__(self, amount: float, security: Security):
        self._amount = amount
        self._security = security

    @property
    def amount(self):
        return self._amount

    @property
    def security(self):
        return self._security

    def withdraw(self, amount: float):
        if amount > self._amount:
            raise UserWarning("Insufficient {} funds.".format(self._security))
        else:
            self._amount -= amount

    def deposit(self, amount: float):
        self._amount += amount


def calculate_optimal_returns(stock_data: StockData):
    btc_holdings = Holdings(20, "BTC")
    ltc_holdings = Holdings(1000, "LTC")
    base_ltc = 1000
    mult = 1
    ltc = []
    btc = []
    close_prices_LTCBTC = [candle.get_price().close_price for candle in stock_data.candles]

    for prev_price, next_price in list(zip(close_prices_LTCBTC[0:-1], close_prices_LTCBTC[1:])):
        amount = 70
        if (next_price - prev_price) > 0:
            ltc_holdings, btc_holdings = buy(which_security=ltc_holdings, with_security=btc_holdings,
                                             at_price=prev_price,
                                             amount=amount)
            # mult * abs(base_ltc * (next_price - prev_price) / prev_price)
        elif (next_price - prev_price) < 0:
            ltc_holdings, btc_holdings = sell(which_security=ltc_holdings, for_security=btc_holdings,
                                              at_price=prev_price,
                                              amount=amount)
        else:
            hold()
        ltc.append(copy(ltc_holdings))
        btc.append(copy(btc_holdings))
    gained_btc = btc[-1].amount - btc[0].amount
    gained_ltc = ltc[-1].amount - ltc[0].amount + gained_btc / close_prices_LTCBTC[-1]
    percent_gain = gained_ltc / base_ltc
    buy_and_hold_percent_gain = (close_prices_LTCBTC[-1] - close_prices_LTCBTC[0]) / close_prices_LTCBTC[0]
    print("Percent gain: {}".format(percent_gain))
    print("Buy and hold percent gain: {}".format(buy_and_hold_percent_gain))
    print("Gained LTC: {}".format(gained_ltc))

    return ltc, btc


def buy(which_security: Holdings, with_security: Holdings, at_price: float, amount: float) -> Tuple[Holdings, Holdings]:
    with_security.withdraw(amount * at_price)
    which_security.deposit(amount)
    return which_security, with_security


def sell(which_security: Holdings, for_security: Holdings, at_price: float, amount: float) -> Tuple[Holdings, Holdings]:
    which_security.withdraw(amount)
    for_security.deposit(amount * at_price)
    return which_security, for_security


def hold() -> None:
    return None


if __name__ == "__main__":
    stock_data = load_from_disk(
        '/home/orphefs/Documents/Code/autotrader/autotrader/data/_data_01_Oct,_2017_10_Oct,_2017_LTCBTC.dill')
    ltc, btc = calculate_optimal_returns( stock_data=stock_data)
    fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)

    plot_candlesticks(ax[0], stock_data)
    plot_returns(ax[1], stock_data, [r.amount for r in ltc])
    plot_returns(ax[2], stock_data, [r.amount for r in btc])
    plt.show()

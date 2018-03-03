from plotting.plot_candles import plot_candlesticks, plot_returns
from tools.downloader import StockData, load_from_disk
import matplotlib.pyplot as plt


def calculate_reference_returns(start_amount: float, stock_data: StockData):
    threshold = 5e-5
    amount = 1.0
    close_prices = [candle.get_price().close_price for candle in stock_data.candles]
    returns = []

    for prev_price, next_price in list(zip(close_prices[0:-1], close_prices[1:])):
        if (next_price - prev_price) > threshold / 2:
            a = buy(start_amount, amount)
        elif (prev_price - next_price) < -threshold / 2:
            a = sell(start_amount, amount)
        else:
            a = hold(start_amount, amount)
        returns.append(a)
    print(returns)
    return returns


def buy(start_amount: float, amount: float) -> float:
    return start_amount - amount


def sell(start_amount: float, amount: float) -> float:
    return start_amount + amount


def hold(start_amount: float, amount: float) -> float:
    return start_amount


if __name__ == "__main__":
    stock_data = load_from_disk(
        '/home/orphefs/Documents/Code/autotrader/autotrader/data/_data_01_Oct,_2017_10_Oct,_2017_LTCBTC.dill')
    returns = calculate_reference_returns(start_amount=100.0, stock_data=stock_data)
    fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)

    plot_candlesticks(ax[0], stock_data)
    plot_returns(ax[1], stock_data, returns)
    plt.show()

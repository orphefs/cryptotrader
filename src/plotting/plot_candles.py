import matplotlib
import matplotlib.pyplot as plt

from typing import List

from matplotlib.axis import Axis

from containers.candle import Candle
from logic.ground_truth import load_from_disk


def plot(ax: Axis, data: List[Candle]):

    ax.scatter(
        y=[candle.get_price().close_price for candle in data],
        x=[candle.get_time().close_time.as_datetime() for candle in data],
               )

if __name__=='__main__':
    candles = load_from_disk('/home/orphefs/Documents/Code/autotrader/autotrader/data/_data_01_Oct,_2017_10_Oct,_2017_LTCBTC.dill')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plot(ax, candles)
    plt.show()

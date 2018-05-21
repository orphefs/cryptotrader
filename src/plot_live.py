import os

from matplotlib import pyplot as plt

import definitions
from live_logic.portfolio import Portfolio
from plotting.plot_candles import custom_plot


def postprocess():
    # TODO: Plot break-in period and annotate with profits
    portfolio = Portfolio.load_from_disk(os.path.join(definitions.DATA_DIR, "portfolio.dill"))
    portfolio.compute_performance()
    custom_plot(portfolio, None)
    print(portfolio._point_stats['base_index_pct_change'])
    print(portfolio._point_stats['total_pct_change'])

    plt.show()

if __name__ == '__main__':
    postprocess()
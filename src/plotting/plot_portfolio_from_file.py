from argparse import ArgumentParser

import matplotlib.pyplot as plt

from src.containers.portfolio import Portfolio
from src.plotting.plot_candles import custom_plot
from src.analysis_tools.run_metadata import FullPaths


def main(path_to_portfolio_dill: str):
    predicted_portfolio = Portfolio.load_from_disk(path_to_portfolio_dill)
    predicted_portfolio.compute_performance()
    custom_plot(portfolio=predicted_portfolio, strategy=None, title='Backtesting run portfolio_df')
    plt.show()


if __name__ == '__main__':
    parser = ArgumentParser(description="Convert metadata dill into csv")
    parser.add_argument("-i", dest="input_filename", required=False,
                        help="input .dill", action=FullPaths)
    args = parser.parse_args()
    print("Input from {}".format(args.input_filename))
    main(args.input_filename)

import os

from src import definitions
from src.live_logic.portfolio import Portfolio


def convert_portfolio_to_csv():
    portfolio = Portfolio.load_from_disk(os.path.join(definitions.DATA_DIR, "portfolio_df.dill"))
    portfolio.compute_performance()
    portfolio.convert_to_csv()


if __name__ == '__main__':
    convert_portfolio_to_csv()

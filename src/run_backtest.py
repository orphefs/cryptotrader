import logging
import os
from typing import Tuple

from src import definitions
from src.definitions import DATA_DIR
from src.resource_manager import runner
from src.type_aliases import Path


def run_backtest(trading_pair: str, trade_amount: float, path_to_stock_data: Path,
                 path_to_log: Path = os.path.join(DATA_DIR,"backtest_run.log"),
                 path_to_portfolio: Path = os.path.join(DATA_DIR,"backtest_portfolio.dill")) -> Tuple[Path, Path]:
    "Run algorithm on historical data, simulating the live mode."


    logging.basicConfig(
        filename=path_to_log, filemode='w',
        # stream=sys.stdout,
        level=logging.INFO,
    )

    with runner(trading_pair=trading_pair,
                trade_amount=trade_amount,
                run_type="mock",
                # mock_data_start_time=datetime(2018, 10, 2),
                # mock_data_stop_time=datetime(2018, 10, 5),
                path_to_stock_data=path_to_stock_data,
                path_to_portfolio=path_to_portfolio
                ) as lr:
        lr.run()

    return path_to_portfolio, path_to_log


if __name__ == '__main__':
    run_backtest()

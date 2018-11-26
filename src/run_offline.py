import logging
import os
from typing import Tuple

from src.classification.train_classifier import run_trained_classifier
from src.definitions import DATA_DIR
from src.type_aliases import Path
from src.containers.trading_pair import TradingPair


def run_offline(trading_pair: TradingPair, trade_amount: float, path_to_stock_data: Path,
                path_to_log: Path = os.path.join(DATA_DIR, "offline_run.log"),
                path_to_classifier: Path = os.path.join(DATA_DIR, "classifier.dill"),
                path_to_portfolio: Path = os.path.join(DATA_DIR, "offline_portfolio.dill")) -> Tuple[Path, Path]:
    "Run the live algorithm with test orders (not placing real orders yet)."

    logging.basicConfig(
        filename=path_to_log, filemode='w',
        # stream=sys.stdout,
        level=logging.DEBUG,
    )

    run_trained_classifier(trading_pair=trading_pair,
                           trade_amount=trade_amount,
                           testing_data=path_to_stock_data,
                           classifier=path_to_classifier,
                           path_to_portfolio=path_to_portfolio, )

    return path_to_portfolio, path_to_log


if __name__ == '__main__':
    path_to_portfolio, path_to_log = run_offline("NEOBTC",
                                                 100,
                                                 os.path.join(DATA_DIR, "test", "test_data.dill"),
                                                 os.path.join(DATA_DIR, "offline_run.log"),
                                                 os.path.join(DATA_DIR, "classifier.dill"),
                                                 os.path.join(DATA_DIR, "offline_portfolio.dill"))
    print(path_to_portfolio, path_to_log)

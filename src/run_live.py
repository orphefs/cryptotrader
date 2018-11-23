import logging
import os
from typing import Tuple

from binance.client import Client

from src import definitions
from src.definitions import DATA_DIR
from src.live_logic.market_maker import MarketMaker, TestMarketMaker
from src.resource_manager import runner
from src.type_aliases import Path


def run_live(trading_pair: str, trade_amount: float,
             path_to_log: Path = os.path.join(DATA_DIR, "live_run.log"),
             path_to_portfolio: Path = os.path.join(DATA_DIR, "live_portfolio.dill"),
             ) -> Tuple[Path, Path]:
    "Run live, on real time exchange data."

    logging.basicConfig(
        filename=path_to_log, filemode='w',
        # stream=sys.stdout,
        level=logging.INFO,
    )

    client = Client("VWwsv93z4UHRoJEOkye1oZeqRtYPiaEXqzeG9fem2guMNKKU1tUDTTta9Nm4JZ3x",
                    "L8C3ws3xkxX2AUravH41kfDezrHin2LarC1K8MDnmGM51dRBZwqDpvTOVZ1Qztap")
    market_maker = TestMarketMaker(client, trading_pair, trade_amount)

    with runner(trading_pair=trading_pair,
                trade_amount=trade_amount,
                run_type="live",
                path_to_portfolio=path_to_portfolio,
                path_to_classifier=os.path.join(DATA_DIR, "classifier.dill"),
                market_maker=market_maker,
                ) as lr:
        lr.run()

    return path_to_portfolio, path_to_log


if __name__ == '__main__':
    path_to_portfolio, path_to_log = run_live("XRPBNB",
                                              100,
                                              os.path.join(DATA_DIR, "live_run.log"),
                                              os.path.join(DATA_DIR, "live_portfolio.dill"))
    print(path_to_portfolio, path_to_log)

import logging
import os
import sys
from typing import Tuple

import websocket

from src.containers.trading import BinanceTrading
from src.definitions import DATA_DIR
from src.logging_filter import LoggingFilter
from src.market_maker.ExperimentalMarketMaker import ExperimentalMarketMaker
from src.market_maker.market_maker import MarketMaker, NoopMarketMaker
from src.resource_manager import runner
from src.type_aliases import Path, BinanceClient
from src.containers.trading_pair import TradingPair


def run_live(trading_pair: TradingPair, trade_amount: float,
             path_to_log: Path = os.path.join(DATA_DIR, "live_run.log"),
             path_to_portfolio: Path = os.path.join(DATA_DIR, "live_portfolio.dill"),
             api_key: str = "", api_secret: str = "",
             websocket_client: websocket.WebSocketApp = None) -> Tuple[Path, Path]:
    "Run live, on real time exchange data."

    logging.basicConfig(
        # filename=path_to_log, filemode='w',
        stream=sys.stdout,
        level=logging.INFO,
    )
    logger = logging.getLogger('cryptotrader-api')
    logger.addFilter(LoggingFilter(logging.INFO))

    client = BinanceClient(api_key, api_secret)
    trader = BinanceTrading(client)
    market_maker = NoopMarketMaker(trader, trading_pair, trade_amount)

    with runner(trading_pair=trading_pair,
            trade_amount=trade_amount,
            run_type="live",
            path_to_portfolio=path_to_portfolio,
            path_to_classifier=os.path.join(DATA_DIR, "classifier.dill"), # TODO: change classifier depending on trading pair
            client=client,
            market_maker=market_maker,
            websocket_client = websocket_client,
    ) as lr:
        lr.run()

    return path_to_portfolio, path_to_log


if __name__ == '__main__':
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("cobinhood-api").setLevel(logging.WARNING)

    quantity = 0.001
    assert quantity <= 0.001
    path_to_portfolio, path_to_log = run_live(TradingPair("ETH", "BTC"),
        quantity,
        os.path.join(DATA_DIR, "live_run.log"),
        os.path.join(DATA_DIR, "live_portfolio.dill"))
    print(path_to_portfolio, path_to_log)

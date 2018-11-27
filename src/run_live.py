import logging
import os
from typing import Tuple



from src import definitions
from src.definitions import DATA_DIR
from src.live_logic.market_maker import MarketMaker, TestMarketMaker
from src.resource_manager import runner
from src.type_aliases import Path, BinanceClient, CobinhoodClient
from src.containers.trading_pair import TradingPair


def run_live(trading_pair: TradingPair, trade_amount: float,
             path_to_log: Path = os.path.join(DATA_DIR, "live_run.log"),
             path_to_portfolio: Path = os.path.join(DATA_DIR, "live_portfolio.dill"),
             ) -> Tuple[Path, Path]:
    "Run live, on real time exchange data."

    logging.basicConfig(
        filename=path_to_log, filemode='w',
        # stream=sys.stdout,
        level=logging.INFO,
    )

    # client = BinanceClient("VWwsv93z4UHRoJEOkye1oZeqRtYPiaEXqzeG9fem2guMNKKU1tUDTTta9Nm4JZ3x",
    #                 "L8C3ws3xkxX2AUravH41kfDezrHin2LarC1K8MDnmGM51dRBZwqDpvTOVZ1Qztap")
    client = CobinhoodClient(API_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfdG9rZW5faWQiOiI"
                             "wNDJiNjQ5MC04NDc5LTRlYmYtYThjNy1jZGQxMGRmZWVhZjIiLCJzY29wZSI"
                             "6WyJzY29wZV9leGNoYW5nZV90cmFkZV9yZWFkIiwic2NvcGVfZXhjaGFuZ2V"
                             "fdHJhZGVfd3JpdGUiXSwidXNlcl9pZCI6ImQ1N2YwMzdkLWFiMGMtNDY0My0"
                             "5OGJlLTI5NGI1YzFhMThlMSJ9.-C9f8-yz7rd-16iD_hGEeDhRD1diP9ObCo"
                             "wXajozgTo.V2:4df57bcdf6191fb4423d8726d45849c34f10d6749809009"
                             "70978da0c441a42a6")

    market_maker = MarketMaker(client, trading_pair, trade_amount)

    with runner(trading_pair=trading_pair,
                trade_amount=trade_amount,
                run_type="live",
                path_to_portfolio=path_to_portfolio,
                path_to_classifier=os.path.join(DATA_DIR, "classifier.dill"),
                client=client,
                market_maker=market_maker,
                ) as lr:
        lr.run()

    return path_to_portfolio, path_to_log


if __name__ == '__main__':
    path_to_portfolio, path_to_log = run_live(TradingPair("ETH", "BTC"),
                                              1,
                                              os.path.join(DATA_DIR, "live_run.log"),
                                              os.path.join(DATA_DIR, "live_portfolio.dill"))
    print(path_to_portfolio, path_to_log)

from datetime import datetime
from typing import Union

import tenacity

from src.containers.data_point import PricePoint
from src.containers.order import Order, OrderState
from src.containers.signal import SignalBuy
from src.containers.trading import BinanceTrading
from src.containers.trading_pair import TradingPair
from src.market_maker.mock_trading import MockTrading


class MarketMakerError(RuntimeError):
    pass


def _instantiate_order() -> Order:
    raise NotImplementedError


def _init_signal() -> SignalBuy:
    return SignalBuy(-1, PricePoint(value=None, date_time=datetime.now()))


@tenacity.retry(wait=tenacity.wait_fixed(1))
def get_last_filled_order(trading_pair: TradingPair, trader: Union[BinanceTrading, MockTrading]):
    last_order = trader.get_last_n_orders(trading_pair, 1)[0]
    i = 1
    while last_order.state is not OrderState.filled:
        last_order = trader.get_last_n_orders(trading_pair, i)[-1]
        i += 1
    return last_order
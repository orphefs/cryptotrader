from typing import List, Dict

from backtesting.type_aliases import MilliSeconds


class Trade(object):
    def __init__(self, id: int, price: float, qty: float, time: MilliSeconds, is_buyer_maker: bool,
                 is_best_match: bool):
        self._id = id
        self._price = price
        self._qty = qty
        self._time = time
        self._is_buyer_maker = is_buyer_maker
        self._is_best_match = is_best_match

    @property
    def id(self):
        return self._id

    @property
    def price(self):
        return self._price

    @property
    def qty(self):
        return self._qty

    @property
    def time(self):
        return self._time

    @property
    def is_buyer_maker(self):
        return self._is_buyer_maker

    @property
    def is_best_match(self):
        return self._is_best_match

    @staticmethod
    def from_trade(trade: Dict):
        return Trade(
            id=trade["trade"],
            price=trade["price"],
            qty=trade["qty"],
            time=trade["time"],
            is_buyer_maker=trade["isBuyerMaker"],
            is_best_match=trade["isBestMatch"])

    @staticmethod
    def from_list_of_trades(trades: List[Dict]):
        return [Trade.from_trade(trade) for trade in trades]

from typing import List, Dict

from backtesting.type_aliases import MilliSeconds


class Trade(object):
    def __init__(self, id: int, price: float, qty: float, time: MilliSeconds, is_buyer_maker: bool,
                 is_best_match: bool):
        self.id = id
        self.price = price
        self.qty = qty
        self.time = time
        self.is_buyer_maker = is_buyer_maker
        self.is_best_match = is_best_match

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



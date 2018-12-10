from typing import List

from src.containers.order import Price, Size
from src.containers.trading_pair import TradingPair


class Ord:
    def __init__(self, price: Price, count: int, size: Size):
        self.price = price
        self.count = count
        self.size = size


class Bid(Ord):
    def __repr__(self):
        return "Bid({},{},{})".format(self.price, self.count, self.size)


class Ask(Ord):
    def __repr__(self):
        return "Ask({},{},{})".format(self.price, self.count, self.size)


class OrderBook:
    def __init__(self,
                 trading_pair: TradingPair,
                 bids: List[Bid],
                 asks: List[Ask]):
        self.trading_pair = trading_pair
        self.bids = bids
        self.asks = asks

    @staticmethod
    def from_response(trading_pair: TradingPair, response: dict):
        return OrderBook(
            trading_pair=trading_pair,
            bids=[Bid(Price(bid[0]), int(bid[1]), Size(bid[2]))
                  for bid in response["bids"]],
            asks=[Ask(Price(ask[0]), int(ask[1]), Size(ask[2]))
                  for ask in response["asks"]],
        )

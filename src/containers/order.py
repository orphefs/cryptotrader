from enum import Enum
from typing import Optional

from src.containers.time import MilliSeconds
from src.containers.trading_pair import TradingPair

OrderID = str
TrailingDistance = str
StopPrice = float
Price = float
Source = str
Filled = str
Size = float
EquivalentPrice = float


class Side(Enum):
    bid = "bid"
    ask = "ask"


class OrderState(Enum):
    queued = "queued"
    open = "open"
    partially_filled = "partially_filled"
    filled = "filled"
    cancelled = "cancelled"
    rejected = "rejected"
    pending_cancellation = "pending_cancellation"
    pending_modifications = "pending_modifications"
    triggered = "triggered"


class OrderType(Enum):
    market = "market"
    limit = "limit"
    market_stop = "market_stop"
    limit_stop = "limit_stop"


class Order(object):
    def __init__(self,
                 trading_pair_id: TradingPair,
                 price: Price,
                 type: OrderType,
                 side: Side,
                 size: Size,
                 stop_price: Optional[StopPrice],
                 source: Optional[Source],
                 equivalent_price: Optional[EquivalentPrice],
                 completed_at: Optional[MilliSeconds],
                 timestamp: Optional[MilliSeconds],
                 state: Optional[OrderState],
                 trailing_distance: Optional[TrailingDistance],
                 id: Optional[OrderID],
                 filled: Optional[Filled],
                 ):
        self.equivalent_price = equivalent_price
        self.trading_pair_id = trading_pair_id
        self.stop_price = stop_price
        self.completed_at = completed_at
        self.timestamp = timestamp
        self.price = price
        self.side = side
        self.source = source
        self.state = state
        self.trailing_distance = trailing_distance
        self.type = type
        self.id = id
        self.filled = filled
        self.size = size

    def to_cobinhood_dict(self) -> dict:
        return {
            "trading_pair_id": "{}".format(self.trading_pair_id.as_string_for_cobinhood()),
            "side": "{}".format(self.side.name),
            "type": "{}".format(self.type.name),
            "price": "{}".format(self.price),
            "size": "{}".format(self.size),
        }

    @staticmethod
    def from_cobinhood_response(order: dict):
        return Order(equivalent_price=EquivalentPrice(order["equivalent_price"]),
                     trading_pair_id=TradingPair.from_cobinhood(order["trading_pair_id"]),
                     stop_price=StopPrice(order["stop_price"]),
                     completed_at=MilliSeconds(int(order["completed_at"])),
                     timestamp=MilliSeconds(int(order["timestamp"])),
                     price=Price(order["price"]),
                     side=Side(order["side"]),
                     source=Source(order["source"]),
                     state=OrderState(order["state"]),
                     trailing_distance=TrailingDistance(order["trailing_distance"]),
                     type=OrderType(order["type"]),
                     id=OrderID(order["id"]),
                     filled=Filled(order["filled"]),
                     size=Size(order["size"]),
                     )


"""
    order: object
        eq_price: the equivalance(average) price
            string
        trading_pair_id: trading pair ID
            string
        stop_price: order stop price
            string
        completed_at: order filled time
            ['string', 'null']
        timestamp: order timestamp in milliseconds
            integer
        price: quote price
            string
        side: order side
            enum [bid, ask]
        source: order source
            string
        state: order status
            enum [queued, open, partially_filled, filled, cancelled, rejected, pending_cancellation, pending_modifications, triggered]
        trailing_distance: order trailing distance
            string
        type: order type
            enum [market, limit, market_stop, limit_stop]
        id: order ID
            string
        filled: amount filled in current order
            string
        size: base amount
            string
"""

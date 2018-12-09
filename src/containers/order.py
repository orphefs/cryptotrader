from datetime import datetime
from enum import Enum
from functools import partial
from typing import Optional, Union

from src.containers.signal import SignalBuy, SignalSell
from src.containers.time import MilliSeconds
from src.containers.trading_pair import TradingPair

OrderID = str
TrailingDistance = str
StopPrice = float
Price = float
Source = str
Filled = float
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

    def __new__(cls, *args, **kwargs):
        if not kwargs:  # handle object creation for unpickling
            if args[7] is Side.bid:
                return super().__new__(OrderBuy)
            elif args[7] is Side.ask:
                return super().__new__(OrderSell)
        elif kwargs:
            if kwargs["side"] is Side.bid:
                return super().__new__(OrderBuy)
            elif kwargs["side"] is Side.ask:
                return super().__new__(OrderSell)
        else:
            raise RuntimeError("Argument Side should be Union[Side.bid, Side.ask]"
                               " on Order instantiation.")

    def __copy__(self):
        obj_copy = Order(**self.__dict__)
        return obj_copy

    def __getnewargs__(self):
        return (self.equivalent_price,
                self.trading_pair_id,
                self.stop_price,
                self.completed_at,
                self.completed_at,
                self.timestamp,
                self.price,
                self.side,
                self.source,
                self.state,
                self.trailing_distance,
                self.type,
                self.id,
                self.filled,
                self.size)

    def __init__(self,
                 trading_pair_id: TradingPair,
                 price: Price,
                 type: OrderType,
                 side: Side,
                 size: Size,
                 stop_price: Optional[StopPrice] = None,
                 source: Optional[Source] = None,
                 equivalent_price: Optional[EquivalentPrice] = None,
                 completed_at: Optional[MilliSeconds] = None,
                 timestamp: Optional[MilliSeconds] = None,
                 state: Optional[OrderState] = None,
                 trailing_distance: Optional[TrailingDistance] = None,
                 id: Optional[OrderID] = None,
                 filled: Optional[Filled] = None,
                 ):
        self.equivalent_price = equivalent_price
        self.trading_pair_id = trading_pair_id
        self.stop_price = stop_price
        if completed_at is not None:
            self.completed_at = completed_at.as_datetime()
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

    def __repr__(self):
        return "{}(completed_at={}, " \
               "equivalent_price={}, " \
               "filled={}, " \
               "id={}, " \
               "price={}, " \
               "side={}, " \
               "size={}, " \
               "source={}, " \
               "state={}, " \
               "timestamp={}, " \
               "trading_pair_id={}, " \
               "type={}, " \
               ")".format(
            self.__class__.__name__,
            self.completed_at,
            self.equivalent_price,
            self.filled,
            self.id,
            self.price,
            self.side,
            self.size,
            self.source,
            self.state,
            self.timestamp.as_epoch_time(),
            self.trading_pair_id,
            self.type,
        )

    @staticmethod
    def from_signal(signal: Union[SignalBuy, SignalSell]):
        Ord = partial(Order, trading_pair_id=TradingPair("NotImplemented",
                                                         "NotImplemented"),
                      price=Price(signal.price_point.value),
                      type=OrderType.limit,
                      size=Size(1.0),
                      filled=Filled(1.0),
                      equivalent_price=Price(signal.price_point.value),
                      completed_at=MilliSeconds(signal.price_point.date_time.timestamp()),
                      timestamp=MilliSeconds(signal.price_point.date_time.timestamp())
                      )
        if isinstance(signal, SignalBuy):
            return Ord(side=Side.bid)
        elif isinstance(signal, SignalSell):
            return Ord(side=Side.ask)

    @staticmethod
    def from_cobinhood_response(order: dict):
        if order["side"] == "bid":
            cls = OrderBuy
        elif order["side"] == "ask":
            cls = OrderSell
        else:
            cls = Order
        return cls(
            completed_at=MilliSeconds.from_cobinhood_timestamp(order["completed_at"]),
            equivalent_price=EquivalentPrice(order["eq_price"]),
            filled=Filled(order["filled"]),
            id=OrderID(order["id"]),
            price=Price(order["price"]),
            side=Side(order["side"]),
            size=Size(order["size"]),
            source=Source(order["source"]),
            state=OrderState(order["state"]),
            timestamp=MilliSeconds(int(order["timestamp"])),
            trading_pair_id=TradingPair.from_cobinhood(order["trading_pair_id"]),
            type=OrderType(order["type"]),
        )


class OrderBuy(Order):
    pass


class OrderSell(Order):
    pass


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

from typing import Optional, List

from src.containers.order import Order, OrderID, Price, Size
from src.containers.trading import Trading, Trade
from src.containers.trading_pair import TradingPair
from src.type_aliases import CobinhoodClient




class MockTrading(Trading):
    def __init__(self, client: MockClient):
        super().__init__(client=client)

    def place_order(self, order: Order, ):
        raise NotImplementedError

    def modify_order(self, order_id: OrderID, price: Price, size: Size):
        raise NotImplementedError

    def get_open_orders(self, order_id: Optional[OrderID]) -> List[Order]:
        raise NotImplementedError

    def cancel_order(self, order_id: OrderID):
        raise NotImplementedError

    def get_last_filled_order(self, trading_pair: TradingPair) -> Order:
        raise NotImplementedError

    def get_order_history(self, trading_pair: TradingPair) -> List[Order]:
        raise NotImplementedError

    def get_orders_trades(self, order_id: OrderID):
        raise NotImplementedError

    def get_trades(self) -> List[Trade]:
        raise NotImplementedError



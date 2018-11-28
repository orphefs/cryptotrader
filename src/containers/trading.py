from src.connection.cobinhood_helpers import load_cobinhood_api_token
from src.containers.order import Order, Price, Size
from src.containers.trading_pair import TradingPair
from src.type_aliases import CobinhoodClient, BinanceClient

OrderID = int

from typing import List, Optional, Union, Any


class Trade:
    pass


class Trading:
    def __init__(self, client: Union[CobinhoodClient, BinanceClient]):
        self._client = client

    def place_order(self, order: Order, ):
        raise NotImplementedError

    def modify_order(self, order_id: OrderID, price: Price, size: Size):
        raise NotImplementedError

    def get_open_orders(self, order_id: Optional[OrderID]) -> List[Order]:
        raise NotImplementedError

    def cancel_order(self, order_id: OrderID):
        raise NotImplementedError

    def get_order_history(self, trading_pair: TradingPair) -> List[Order]:
        raise NotImplementedError

    def get_orders_trades(self, order_id: OrderID):
        raise NotImplementedError

    def get_trades(self) -> List[Trade]:
        raise NotImplementedError


class CobinhoodError(RuntimeError):
    pass


class CobinhoodTrading(Trading):
    def __init__(self, client: CobinhoodClient):
        super().__init__(client=client)

    def place_order(self, order: Order) -> Order:
        response = self._client.trading.post_orders(data=order.to_cobinhood_dict())

        if response["success"]:
            return Order.from_cobinhood_response(response["result"]["order"])
        else:
            raise CobinhoodError("Could not place order. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    def modify_order(self, order: Order, price: Price, size: Size) -> bool:
        order.price = price
        order.size = size
        response = self._client.trading.put_orders(order_id=order.id,
                                                   data=order.to_cobinhood_dict())
        if response["success"]:
            return True
        else:
            raise CobinhoodError("Could not modify order. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    def get_open_orders(self, order_id: Optional[OrderID]=None) -> List[Optional[Order]]:
        response = self._client.trading.get_orders(order_id=order_id)

        if response["success"]:
            if isinstance(response["result"]["orders"], list):
                return [Order.from_cobinhood_response(order) for order in response["result"]["orders"]]
        else:
            raise CobinhoodError("There are no result in history to be fetched. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    def cancel_order(self, order_id: OrderID) -> bool:
        response = self._client.trading.cancel_order(order_id)

        if response["success"]:
            return True
        else:
            raise CobinhoodError("Could not cancel order. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    def get_order_history(self, trading_pair: TradingPair) -> List[Order]:

        response = self._client.trading.get_order_history(limit=100)
        if response["success"]:
            pages = response["result"]["total_page"]
            orders = []
            for i in range(0, pages):
                response = self._client.trading.get_order_history(limit=100, page=i)
                orders += response["result"]["orders"]
            return [Order.from_cobinhood_response(order) for order in orders]
        else:
            raise CobinhoodError("Could not fetch order history. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    def get_orders_trades(self, order_id: OrderID):
        raise NotImplementedError

    def get_trades(self) -> List[Trade]:
        raise NotImplementedError


if __name__ == '__main__':
    client = CobinhoodClient(API_TOKEN=load_cobinhood_api_token())
    trader = CobinhoodTrading(client)
    # orders = trader.get_order_history(trading_pair=TradingPair("ETH", "BTC"))
    orders = trader.get_open_orders()
    for order in orders:
        print(order)

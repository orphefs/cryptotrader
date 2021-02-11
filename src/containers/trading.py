import tenacity

from src.connection.binance_helpers import load_binance_api_token
from src.containers.order import Order, Price, Size, OrderID, OrderState
from src.containers.order_book import OrderBook
from src.containers.trading_pair import TradingPair
from src.market_maker.mock_client import MockClient
from src.type_aliases import BinanceClient
from src.logger import logger

from typing import List, Optional, Union


class BinanceError(RuntimeError):
    pass


class Trade:
    pass


class Trading:
    def __init__(self, client: Union[BinanceClient, MockClient]):
        self._client = client

    def place_order(self, order: Order, ) -> Order:
        raise NotImplementedError

    def modify_order(self, order_id: OrderID, price: Price, size: Size) -> bool:
        raise NotImplementedError

    def get_open_orders(self, order_id: Optional[OrderID]) -> List[Optional[Order]]:
        raise NotImplementedError

    def cancel_order(self, order_id: OrderID) -> bool:
        raise NotImplementedError

    def get_last_filled_order(self, trading_pair: TradingPair) -> Order:
        raise NotImplementedError

    def get_order_history(self, trading_pair: TradingPair) -> List[Order]:
        raise NotImplementedError

    def get_orders_trades(self, order_id: OrderID):
        raise NotImplementedError

    def get_trades(self) -> List[Trade]:
        raise NotImplementedError


class BinanceTrading(Trading):
    def __init__(self, client: BinanceClient):
        super().__init__(client=client)

    def place_order(self, order: Order) -> Order:
        response = self._client.trading.post_orders(data=order.to_cobinhood_dict())
        if response["success"]:
            logger.debug("Placed order...")
            return Order.from_cobinhood_response(response["result"]["order"])
        else:
            raise BinanceError("Could not place order. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    @tenacity.retry(wait=tenacity.wait_fixed(1))
    def modify_order(self, order: Order, price: Price, size: Size) -> bool:
        order.price = price
        order.size = size
        response = self._client.trading.put_orders(order_id=order.id,
                                                   data=order.to_cobinhood_dict())
        if response["success"]:
            logger.debug("Modified order...")
            return True
        else:
            raise BinanceError("Could not modify order. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    @tenacity.retry(wait=tenacity.wait_fixed(1))
    def get_open_orders(self, order_id: Optional[OrderID] = None) -> List[Optional[Order]]:
        response = self._client.trading.get_orders(order_id=order_id)

        if response["success"]:
            if "order" in response["result"]:
                order = Order.from_cobinhood_response(response["result"]["order"])
                if order.state is OrderState.open:
                    return [order]
            elif "orders" in response["result"]:
                orders = [Order.from_cobinhood_response(order) for order in response["result"]["orders"]]
                return [order for order in orders if order.state is OrderState.open]
        else:
            raise BinanceError("There are no results in history to be fetched. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    @tenacity.retry(wait=tenacity.wait_fixed(1))
    def cancel_order(self, order_id: OrderID) -> bool:
        response = self._client.trading.delete_orders(order_id)

        if response["success"]:
            logger.debug("Cancelled order...")
            return True
        else:
            raise BinanceError("Could not cancel order. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    @tenacity.retry(wait=tenacity.wait_fixed(1))
    def get_last_n_orders(self, trading_pair: TradingPair, n: int) -> List[Order]:
        response = self._client.trading.get_order_history(trading_pair_id=trading_pair.as_string_for_cobinhood(),
                                                          limit=n, page=0)
        if response["success"]:
            logger.debug("Fetched last order...")
            return [Order.from_cobinhood_response(order) for order in response["result"]["orders"]]
        else:
            raise BinanceError("Could not fetch last n orders. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    @tenacity.retry(wait=tenacity.wait_fixed(1))
    def get_order_history(self, trading_pair: TradingPair) -> List[Order]:
        response = self._client.trading.get_order_history(trading_pair_id=trading_pair.as_string_for_cobinhood(),
                                                          limit=10)
        if response["success"]:
            pages = response["result"]["total_page"]
            orders = []
            for i in range(0, pages):
                response = self._client.trading.get_order_history(
                    trading_pair_id=trading_pair.as_string_for_cobinhood(),
                    limit=100, page=i)
                orders += response["result"]["orders"]
            return [Order.from_cobinhood_response(order) for order in orders]
        else:
            raise BinanceError("Could not fetch order history. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    def get_orderbook(self, trading_pair: TradingPair) -> OrderBook:
        response = self._client.market.get_orderbooks(
            trading_pair_id=trading_pair.as_string_for_cobinhood())
        print(response)

        if response["success"]:
            logger.debug("Fetched last order...")
            return OrderBook.from_response(trading_pair, response["result"]["orderbook"])
        else:
            raise BinanceError("Could not fetch last n orders. "
                                 "Reason: {}".format(response["error"]["error_code"]))

    def get_orders_trades(self, order_id: OrderID):
        raise NotImplementedError

    def get_trades(self) -> List[Trade]:
        raise NotImplementedError


if __name__ == '__main__':
    client = BinanceClient(API_TOKEN=load_binance_api_token())
    trader = BinanceTrading(client)
    trading_pair = TradingPair("ETH", "BTC")
    order_book = trader.get_orderbook(trading_pair)
    for ask in order_book.asks:
        print(ask)

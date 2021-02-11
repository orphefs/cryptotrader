from datetime import datetime
from typing import List, Union

from src.containers.intersection_point import SignalBuy
from src.containers.order import Order
from src.containers.signal import SignalSell
from src.containers.data_point import PricePoint, Price
from src.containers.portfolio import Portfolio
from src.definitions import DATA_DIR
from src.type_aliases import Path, BinanceClient
import os


def load_binance_api_token():
    with open(os.path.join(DATA_DIR, "api_keys", "binance_api_key.txt"), 'r') as infile:
        token = infile.readline().strip("\n")
    return token


def convert_orders_to_signals(orders: List[dict]) -> List[Union[SignalBuy, SignalSell]]:
    signals = []
    for order in orders:
        if "state" in order:
            if order["state"] == "filled":
                if order["side"] == "bid":
                    signals.append(SignalBuy(signal=-1,
                                             price_point=PricePoint(value=Price(order["eq_price"]),
                                                              date_time=datetime.fromtimestamp(
                                                                  order["timestamp"] / 1000))))
                if order["side"] == "ask":
                    signals.append(SignalSell(signal=1,
                                              price_point=PricePoint(value=Price(order["eq_price"]),
                                                               date_time=datetime.fromtimestamp(
                                                                   order["timestamp"] / 1000))))

            else:
                continue

    return signals


def order_signals_by_timestamp(signals: List[Union[SignalBuy, SignalSell]]):
    return sorted(signals, key=lambda x: x.price_point.date_time, reverse=False)


def construct_portfolio_from_exchange_order_data(signals: List[Union[SignalBuy, SignalSell]],
                                                 path_to_exchange_portfolio: Path) -> Path:
    portfolio = Portfolio(initial_capital=0.0091,
                          trade_amount=0.02)
    for signal in signals:
        portfolio.update(Order.from_signal(signal))
    portfolio.compute_performance()
    portfolio.save_to_disk(path_to_exchange_portfolio)
    return path_to_exchange_portfolio


def get_exchange_orders() -> List[dict]:
    token = load_binance_api_token()
    client = BinanceClient(API_TOKEN=token)
    data = client.trading.get_order_history(limit=100)
    pages = data["result"]["total_page"]
    orders = []
    for i in range(0, pages):
        data = client.trading.get_order_history(limit=100, page=i)
        orders += data["result"]["orders"]
    return orders


if __name__ == '__main__':
    orders = get_exchange_orders()
    signals = convert_orders_to_signals(orders)
    signals = order_signals_by_timestamp(signals)
    construct_portfolio_from_exchange_order_data(signals,
                                                 os.path.join(DATA_DIR, "exchange_portfolio_df.dill"))

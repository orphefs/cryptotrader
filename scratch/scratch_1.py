import json
from binance.client import Client


def plot_historical_data():
    pass


def main():
    client = Client("", "")
    klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")
    print(klines)


if __name__ == "__main__":
    main()

from typing import List

from backtesting.type_aliases import MilliSeconds


class Time(object):
    def __init__(self, open_time: MilliSeconds, close_time: MilliSeconds):
        self._open_time = open_time
        self._close_time = close_time

    def __repr__(self):
        return "Time(open_time={}, close_time={})".format(self._open_time, self._close_time)


class Price(object):
    def __init__(self, open_price: float, high_price: float, low_price: float, close_price: float):
        self._open_price = open_price
        self._high_price = high_price
        self._low_price = low_price
        self._close_price = close_price

    def __repr__(self):
        return "Price(open_price={}, high_price={}, low_price={}, close_price={} )".format(self._open_price,
                                                                                           self._high_price,
                                                                                           self._low_price,
                                                                                           self._close_price,
                                                                                           )


class Volume(object):
    def __init__(self, volume: int, taker_buy_base_asset_volume: int, taker_buy_quote_asset_volume: int,
                 quote_asset_volume: int, number_of_trades: int):
        self._volume = volume
        self._taker_buy_base_asset_volume = taker_buy_base_asset_volume
        self._taker_buy_quote_asset_volume = taker_buy_quote_asset_volume
        self._quote_asset_volume = quote_asset_volume
        self._number_of_trades = number_of_trades

    def __repr__(self):
        return "Volume(volume={}, taker_buy_base_asset_volume={}, " \
               "taker_buy_quote_asset_volume={}, quote_asset_volume={}, " \
               "number_of_trades={},  )".format(self._volume,
                                                self._taker_buy_base_asset_volume,
                                                self._taker_buy_quote_asset_volume,
                                                self._quote_asset_volume,
                                                self._number_of_trades,
                                                )


class Candle(object):
    def __init__(self, price: Price, volume: Volume, time: Time):
        self._price = price
        self._volume = volume
        self._time = time

    def __repr__(self):
        return "Candle({},{},{})".format(self.price, self.volume, self.time)

    @staticmethod
    def from_list_of_klines(klines: List[List]) -> List[Candle]:
        return [Candle(
            price=Price(
                open_price=kline[1],
                high_price=kline[2],
                low_price=kline[3],
                close_price=kline[4],
            ),
            volume=Volume(
                volume=kline[5],
                taker_buy_base_asset_volume=kline[9],
                taker_buy_quote_asset_volume=kline[10],
                quote_asset_volume=kline[7],
                number_of_trades=kline[8],
            ),
            time=Time(
                open_time=kline[0],
                close_time=kline[6],
            )

        ) for kline in klines]


if __name__ == "__main__":
    from binance.client import Client

    client = Client("", "")
    klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")
    print(klines)

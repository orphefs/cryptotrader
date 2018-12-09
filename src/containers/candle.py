from typing import List, Any, Optional
import numpy as np
from datetime import datetime

from src.containers.time import Time, MilliSeconds
from src.type_aliases import Exchange


class Price(object):
    def __init__(self, open_price: float, high_price: float, low_price: float, close_price: float):
        self._open_price = open_price
        self._high_price = high_price
        self._low_price = low_price
        self._close_price = close_price

    @property
    def open_price(self):
        return self._open_price

    @property
    def high_price(self):
        return self._high_price

    @property
    def low_price(self):
        return self._low_price

    @property
    def close_price(self):
        return self._close_price

    def __repr__(self):
        return "Price(open_price={}, high_price={}, low_price={}, close_price={} )".format(self._open_price,
                                                                                           self._high_price,
                                                                                           self._low_price,
                                                                                           self._close_price,
                                                                                           )


class Volume(object):
    def __init__(self, volume: float, taker_buy_base_asset_volume: float, taker_buy_quote_asset_volume: float,
                 quote_asset_volume: float, number_of_trades: int):
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

    @property
    def volume(self):
        return self._volume

    @property
    def taker_buy_base_asset_volume(self):
        return self._taker_buy_base_asset_volume

    @property
    def taker_buy_quote_asset_volume(self):
        return self._taker_buy_quote_asset_volume

    @property
    def quote_asset_volume(self):
        return self._quote_asset_volume

    @property
    def number_of_trades(self):
        return self._number_of_trades


class Candle(object):
    def __init__(self, price: Optional[Price], volume: Optional[Volume], time: Time):
        self._price = price
        self._volume = volume
        self._time = time

    def get_price(self):
        return self._price

    def get_close_price(self):
        return self._price.close_price

    def get_open_price(self):
        return self._price.open_price

    def get_number_of_trades(self):
        return self._volume.number_of_trades

    def get_volume(self):
        return self._volume.volume

    def get_time(self):
        return self._time

    def get_close_time_as_datetime(self):
        return self._time.close_time.as_datetime()

    def __repr__(self):
        return "Candle({},\n{},\n{})".format(self._price, self._volume, self._time)

    @staticmethod
    def from_binance_kline(kline: List[Any]):
        return Candle(
            price=Price(
                open_price=float(kline[1]),
                high_price=float(kline[2]),
                low_price=float(kline[3]),
                close_price=float(kline[4]),
            ),
            volume=Volume(
                volume=float(kline[5]),
                taker_buy_base_asset_volume=float(kline[9]),
                taker_buy_quote_asset_volume=float(kline[10]),
                quote_asset_volume=float(kline[7]),
                number_of_trades=int(kline[8]),
            ),
            time=Time(
                open_time=MilliSeconds(int(kline[0])),
                close_time=MilliSeconds(int(kline[6])),
            )

        )

    @staticmethod
    def from_cobinhood_kline(kline: dict):
        return Candle(
            price=Price(
                open_price=float(kline["open"]),
                high_price=float(kline["high"]),
                low_price=float(kline["low"]),
                close_price=float(kline["close"]),
            ),
            volume=Volume(
                volume=float(kline["volume"]),
                taker_buy_base_asset_volume=np.nan,
                taker_buy_quote_asset_volume=np.nan,
                quote_asset_volume=np.nan,
                number_of_trades=np.nan,
            ),
            time=Time(
                open_time=MilliSeconds(None),
                close_time=MilliSeconds(int(kline["timestamp"])),
            ),
        )

    @staticmethod
    def from_list_of_klines(klines: List, source: Exchange):
        if source.name is "BINANCE":
            return [Candle.from_binance_kline(kline) for kline in klines]
        elif source.name is "COBINHOOD":
            return [Candle.from_cobinhood_kline(kline) for kline in klines]
        else:
            raise ValueError("You need to specify the source (Exchange) from which to download the data.")


def instantiate_1970_candle():
    return Candle(price=None, volume=None, time=Time(open_time=MilliSeconds(int(datetime(1970, 1, 1).timestamp())),
                                                     close_time=MilliSeconds(int(datetime(1970, 1, 1).timestamp()))))


if __name__ == "__main__":
    from binance.client import Client

    client = Client("", "")
    klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "3 Dec, 2017")
    candles = Candle.from_list_of_klines(klines)
    print(candles[0])
    print(len(candles))

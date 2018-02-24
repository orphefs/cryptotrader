from backtesting.type_aliases import MilliSeconds


class Time(object):
    def __init__(self, open_time: MilliSeconds, close_time: MilliSeconds):
        self._open_time = open_time
        self._close_time = close_time


class Price(object):
    def __init__(self, open_price: float, high_price: float, low_price: float, close_price: float):
        self._open_price = open_price
        self._high_price = high_price
        self._low_price = low_price
        self._close_price = close_price


class Volume(object):
    def __init__(self, volume: int, taker_buy_base_asset_volume: int, taker_buy_quote_asset_volume: int,
                 quote_asset_volume: int, number_of_trades: int ):
        self._volume = volume
        self._taker_buy_base_asset_volume = taker_buy_base_asset_volume
        self._taker_buy_quote_asset_volume = taker_buy_quote_asset_volume
        self._quote_asset_volume = quote_asset_volume
        self._number_of_trades = number_of_trades


class Candle(object):
    def __init__(self, price: Price, volume: Volume, time: Time ):
        self._price = price
        self._volume = volume
        self._time = time


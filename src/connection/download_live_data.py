from datetime import timedelta, datetime, timezone
from typing import List, Union


from src.connection.connection_handling import retry_on_network_error
from src.connection.constants import binance_sampling_rate_mappings, cobinhood_sampling_rate_mappings
from src.connection.helpers import DownloadingError
from src.containers.candle import Candle
from src.containers.trading_pair import TradingPair
from src.type_aliases import Exchange, BinanceClient


def _download_live_data_from_binance(trading_pair: TradingPair, sampling_period: timedelta,
                                     client: BinanceClient) -> Candle:
    klines = client.get_historical_klines(trading_pair.as_string_for_binance(),
                                          binance_sampling_rate_mappings[
                                              sampling_period.total_seconds()],
                                          "30 minutes ago GMT")
    return Candle.from_list_of_klines(klines, Exchange.BINANCE)[-1]



def _download_live_data_from_exchange(trading_pair: TradingPair, sampling_period: timedelta,
                                      client: Union[BinanceClient]) -> Candle:
    if isinstance(client, BinanceClient):

        return _download_live_data_from_binance(trading_pair, sampling_period, client)

    else:
        raise DownloadingError("Invalid client object.")


@retry_on_network_error
def download_live_data(client: Union[BinanceClient], trading_pair: TradingPair,
                       sampling_period: timedelta, lags: int) -> Candle:
    candle = _download_live_data_from_exchange(trading_pair, sampling_period, client)

    if isinstance(candle, list):
        raise DownloadingError("Only one candle is needed for the live run downloader")
    return candle
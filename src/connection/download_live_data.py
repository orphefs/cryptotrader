from datetime import timedelta, datetime, timezone
from typing import List, Union

from binance.client import Client as BinanceClient
from cobinhood_api import Cobinhood as CobinhoodClient

from src.connection.connection_handling import retry_on_network_error
from src.connection.constants import binance_sampling_rate_mappings, cobinhood_sampling_rate_mappings
from src.connection.helpers import DownloadingError
from src.containers.candle import Candle
from src.containers.trading_pair import TradingPair
from src.type_aliases import Exchange


def _download_live_data_from_binance(trading_pair: TradingPair, api_interval_callback: timedelta,
                                     client: BinanceClient) -> List[Candle]:
    klines = client.get_historical_klines(trading_pair.as_string_for_binance(),
                                          binance_sampling_rate_mappings[
                                              api_interval_callback.total_seconds()],
                                          "30 minutes ago GMT")
    return Candle.from_list_of_klines(klines, Exchange.BINANCE)


def _download_live_data_from_cobinhood(trading_pair: TradingPair, api_interval_callback: timedelta,
                                       client: CobinhoodClient) -> List[Candle]:
    klines = client.chart.get_candles(trading_pair_id=trading_pair,
                                      start_time=round(datetime.now(timezone.utc).timestamp() * 1000),
                                      end_time=round(datetime.now(timezone.utc).timestamp() * 1000),
                                      timeframe=cobinhood_sampling_rate_mappings[
                                          api_interval_callback.total_seconds()],
                                      )
    if "error" in klines:
        raise DownloadingError("{}".format(klines["error"]["error_code"]))
    else:
        pass

    return Candle.from_list_of_klines(klines["result"]["candles"], Exchange.COBINHOOD)


def _download_live_data_from_exchange(trading_pair: TradingPair, api_interval_callback: timedelta,
                                      client: Union[BinanceClient, CobinhoodClient]) -> List[Candle]:
    if isinstance(client, BinanceClient):

        return _download_live_data_from_binance(trading_pair, api_interval_callback, client)
    elif isinstance(client, CobinhoodClient):
        return _download_live_data_from_cobinhood(trading_pair, api_interval_callback, client)
    else:
        raise DownloadingError("Invalid client object.")


@retry_on_network_error
def download_live_data(client: Union[BinanceClient, CobinhoodClient], trading_pair: TradingPair,
                       api_interval_callback: timedelta, lags: int) -> Candle:
    candle = _download_live_data_from_exchange(trading_pair, api_interval_callback, client)[-1]
    print(candle)
    if isinstance(candle, list):
        raise DownloadingError("Only one candle is needed for the live run downloader")
    return candle
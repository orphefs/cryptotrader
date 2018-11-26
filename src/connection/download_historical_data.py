from datetime import timedelta
from typing import List, Union

import dill

from src.connection.constants import binance_sampling_rate_mappings, cobinhood_sampling_rate_mappings
from src.connection.helpers import DownloadingError

dill.dill._reverse_typemap['ClassType'] = type



from src.containers.candle import Candle
from src.containers.time_windows import TimeWindow, Date
from src.type_aliases import Exchange, BinanceClient, CobinhoodClient
from src.containers.trading_pair import TradingPair


def _download_historical_data_from_binance(time_window: TimeWindow, trading_pair: TradingPair, api_interval_callback: timedelta,
                                           client: BinanceClient) -> List[Candle]:
    klines = client.get_historical_klines(trading_pair.as_string_for_binance(),
                                          binance_sampling_rate_mappings[api_interval_callback.total_seconds()],
                                          Date(time_window.start_datetime).as_string(),
                                          Date(time_window.end_datetime).as_string())

    return Candle.from_list_of_klines(klines, Exchange.BINANCE)


def _download_historical_data_from_cobinhood(time_window: TimeWindow, trading_pair: TradingPair,
                                             api_interval_callback: timedelta,
                                             client: CobinhoodClient) -> \
        List[Candle]:
    klines = client.chart.get_candles(trading_pair_id=trading_pair.as_string_for_cobinhood(),
                                      start_time=round(time_window.start_datetime.timestamp() * 1000),
                                      end_time=round(time_window.end_datetime.timestamp() * 1000),
                                      timeframe=cobinhood_sampling_rate_mappings[api_interval_callback.total_seconds()],
                                      )
    if "error" in klines:
        raise DownloadingError("{}".format(klines["error"]["error_code"]))
    else:
        pass

    return Candle.from_list_of_klines(klines["result"]["candles"], Exchange.COBINHOOD)


def _download_historical_data_from_exchange(time_window: TimeWindow, trading_pair: TradingPair,
                                            api_interval_callback: timedelta,
                                            client: Union[BinanceClient, CobinhoodClient]) -> List[Candle]:
    if isinstance(client, BinanceClient):

        return _download_historical_data_from_binance(time_window, trading_pair,
                                                      api_interval_callback,
                                                      client)
    elif isinstance(client, CobinhoodClient):
        return _download_historical_data_from_cobinhood(time_window, trading_pair,
                                                        api_interval_callback,
                                                        client)
    else:
        raise DownloadingError("Invalid client object.")



import logging
import warnings
from collections import defaultdict
from typing import DefaultDict, List

import numpy as np
import pandas as pd

from src.containers.signal import SignalBuy, SignalSell
from src.containers.candle import Candle
from src.containers.data_point import PricePoint
from src.containers.stock_data import StockData
from src.feature_extraction.technical_indicator import TechnicalIndicator


def extract_indicators_from_stock_data(stock_data, list_of_technical_indicators):
    training_data = defaultdict(list)
    for candle in stock_data.candles:
        logging.debug("Running update_indicators() on candle {}\n".format(candle))
        training_data = update_indicators(candle, training_data, list_of_technical_indicators)
    return training_data


def convert_to_pandas(predictors: defaultdict(list), labels: list = None):
    if labels is not None:
        lst = [np.nan] + [trading_signal.signal for trading_signal in labels]
    else:
        lst = [0] * len(list(predictors.values())[0])
    predictors['labels'] = lst
    df = pd.DataFrame(predictors).dropna()
    return df[[col for col in df.columns if col != 'labels']], df['labels']


def get_training_labels(stock_data: StockData):
    training_labels = []
    for current_candle, next_candle in list(zip(stock_data.candles[0:], stock_data.candles[1:])):

        if next_candle.get_close_price() > current_candle.get_close_price():
            training_labels.append(SignalBuy(-1, PricePoint(value=current_candle.get_close_price(),
                                                            date_time=current_candle.get_close_time_as_datetime())))
        else:
            training_labels.append(SignalSell(1, PricePoint(value=current_candle.get_close_price(),
                                                            date_time=current_candle.get_close_time_as_datetime())))
    return training_labels


def update_indicators(candle: Candle, training_data: DefaultDict,
                      list_of_technical_indicators: List[TechnicalIndicator]):
    for indicator in list_of_technical_indicators:
        if indicator.technical_indicator_name is None:
            warnings.warn("You must explicitly specify a unique name for the technical indicator "
                          "(property technical_indicator_name)", NoUniqueNameforCompoundTechnicalIndicatorWarning)
        indicator.update(candle)
        indicator_key = str(indicator)
        training_data[indicator_key].append(indicator.result)
        logging.debug(
            "\n\n\n\n Candle: \n {} \n\n Indicator: {} \n Result: {}".format(candle, indicator, indicator.result))
    return training_data


def extract_indicator_from_candle(candle, list_of_technical_indicators):
    training_data = defaultdict(list)
    logging.debug("Running update_indicators() on candle {}\n".format(candle))
    training_data = update_indicators(candle, training_data, list_of_technical_indicators)
    return training_data


def timeshift_predictions(labels: pd.Series) -> pd.Series:
    # Shift label by 1 minute to associate previous prediction with next price move - Experimental
    ser = pd.Series(np.roll(labels, -1))
    ser.index += 1
    return ser


class NoUniqueNameforCompoundTechnicalIndicatorWarning(UserWarning):
    pass
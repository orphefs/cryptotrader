from collections import defaultdict

import numpy as np
import pandas as pd

from src.backtesting_logic.logic import Buy, Sell
from src.containers.data_point import PricePoint
from src.containers.stock_data import StockData


def extract_indicators_from_stock_data(stock_data, list_of_technical_indicators):
    training_data = defaultdict(list)
    for candle in stock_data.candles:
        for indicator in list_of_technical_indicators:
            indicator.update(candle)
            indicator_key = str(indicator)
            training_data[indicator_key].append(indicator.result)
    return training_data


def get_training_labels(stock_data: StockData):
    training_labels = []
    for current_candle, next_candle in list(zip(stock_data.candles[0:], stock_data.candles[1:])):

        if next_candle.get_close_price() > current_candle.get_close_price():
            training_labels.append(Buy(-1, PricePoint(value=current_candle.get_close_price(),
                                                      date_time=current_candle.get_close_time_as_datetime())))
        else:
            training_labels.append(Sell(1, PricePoint(value=current_candle.get_close_price(),
                                                      date_time=current_candle.get_close_time_as_datetime())))
    return training_labels


def convert_to_pandas(predictors: defaultdict(list), labels: list = None):
    if labels is not None:
        lst = [np.nan] + [trading_signal.signal for trading_signal in labels]
    else:
        lst = [0] * len(list(predictors.values())[0])
    predictors['labels'] = lst
    df = pd.DataFrame(predictors).dropna()
    return df[[col for col in df.columns if col != 'labels']], df['labels']


def extract_indicator_from_candle(candle, list_of_technical_indicators):
    training_data = defaultdict(list)
    for indicator in list_of_technical_indicators:
        indicator.update(candle)
        indicator_key = str(indicator)
        training_data[indicator_key].append(indicator.result)
    return training_data

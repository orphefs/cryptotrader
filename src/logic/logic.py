import numpy as np
from typing import List, Union
import pandas as pd
from datetime import datetime, timedelta

Price = float


class DataPoint(object):
    def __init__(self, value: Price, index: datetime):
        self._value = value
        self._index = index

    @property
    def value(self):
        return self._value

    @property
    def index(self):
        return self._index

    def __repr__(self):
        return "DataPoint({},{})".format(self._value, self._index)


class TimeSeries(pd.Series):
    def __init__(self, x: List[datetime], y: Union[List[Price], np.ndarray]):
        super().__init__(data=y, index=x)
        self._sampling_rate = np.median(np.diff(x))

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @staticmethod
    def from_datapoints(data_points: List[DataPoint]):
        return TimeSeries(x=[data_point.index for data_point in data_points],
                          y=[data_point.value for data_point in data_points])


class IntersectionPoint(object):
    def __init__(self, data_point: DataPoint, intersecting_time_series: List[TimeSeries], tolerance: float):
        self._data_point = data_point
        self._intersecting_time_series = intersecting_time_series
        self._tolerance = tolerance

    @property
    def data_point(self):
        return self._data_point

    @property
    def tolerance(self):
        return self._tolerance

    @property
    def intersecting_time_series(self):
        return self._intersecting_time_series

    def __repr__(self):
        return "IntersectionPoint(data_point={}, tolerance={})".format(self._data_point, self._tolerance)


def get_intersection_points(time_series_a: TimeSeries,
                            time_series_b: TimeSeries, tolerance: float) -> List[IntersectionPoint]:
    ser = np.abs(time_series_b - time_series_a)
    intersection_indices = ser[(ser > -tolerance / 2) & (ser < tolerance / 2)].index

    return [IntersectionPoint(data_point=DataPoint(time_series_a[index], index),
                              intersecting_time_series=[time_series_a, time_series_b],
                              tolerance=tolerance) for index in intersection_indices]


def moving_average(window_size: timedelta, time_series: TimeSeries) -> TimeSeries:
    window_size_int = window_size // time_series.sampling_rate
    weights = np.repeat(1.0, window_size_int) / window_size_int
    sma = np.convolve(np.array(time_series), weights, 'valid')
    return TimeSeries(x=time_series.index[window_size_int - 1:], y=sma)


if __name__ == '__main__':
    time_series_a = TimeSeries(x=[datetime(2017, 1, d) for d in range(1, 30)], y=np.random.normal(5, 1, 29))
    time_series_b = TimeSeries(x=[datetime(2017, 1, d) for d in range(1, 30)], y=np.random.normal(6, 3, 29))
    avg_time_series_a = moving_average(timedelta(days=5), time_series_a)
    avg_time_series_b = moving_average(timedelta(days=5), time_series_b)
    intersection_points = get_intersection_points(avg_time_series_a, avg_time_series_b, 1)
    for intersection_point in intersection_points:
        print(intersection_point)

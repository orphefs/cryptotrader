from datetime import datetime
from typing import List, Union, Optional

import numpy as np
import pandas as pd

from src.containers.data_point import Price, PricePoint


def _compute_sampling_rate(x: Optional[List[datetime]]) -> datetime:
    if x is not None:
        return np.median(np.diff(x))


class TimeSeries(pd.Series):
    def __init__(self, x: Optional[List[datetime]] = None,
                 y: Optional[Union[List[Price], np.ndarray]] = None):
        super().__init__(data=y, index=x)
        # TODO: Fix sampling rate implementation with new pandas version
        # self._sampling_rate = _compute_sampling_rate(x)

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @staticmethod
    def from_datapoints(data_points: List[PricePoint]):
        return TimeSeries(x=[data_point.date_time for data_point in data_points],
                          y=[data_point.value for data_point in data_points])

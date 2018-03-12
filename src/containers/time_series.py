from datetime import datetime
from typing import List, Union

import pandas as pd
import numpy as np
from containers.data_point import Price, DataPoint


class TimeSeries(pd.Series):
    def __init__(self, x: List[datetime], y: Union[List[Price], np.ndarray]):
        super().__init__(data=y, index=x)
        self._sampling_rate = np.median(np.diff([time.as_epoch_time() for time in x]))

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @staticmethod
    def from_datapoints(data_points: List[DataPoint]):
        return TimeSeries(x=[data_point.date_time for data_point in data_points],
                          y=[data_point.value for data_point in data_points])
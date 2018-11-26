import datetime
from typing import Optional


class MilliSeconds(object):
    def __init__(self, time: Optional[int]):
        self._time = time

    def as_epoch_time(self) -> int:
        return self._time

    def as_datetime(self) -> Optional[datetime.datetime]:
        if self._time is None:
            return None
        else:
            return datetime.datetime.fromtimestamp(self._time / 1000)


class Time(object):
    def __init__(self, open_time: MilliSeconds, close_time: MilliSeconds):
        self._open_time = open_time
        self._close_time = close_time

    @property
    def open_time(self):
        return self._open_time

    @property
    def close_time(self):
        return self._close_time

    def __repr__(self):
        return "Time(open_time={}, close_time={})".format(self._open_time.as_datetime(),
                                                          self._close_time.as_datetime())

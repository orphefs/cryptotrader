import datetime


class MilliSeconds(object):
    def __init__(self, time: int):
        self._time = time

    def as_epoch_time(self) -> int:
        return self._time

    def as_datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self._time/1000)


class Time(object):
    def __init__(self, open_time: MilliSeconds, close_time: MilliSeconds):
        self._open_time = open_time
        self._close_time = close_time

    def __repr__(self):
        return "Time(open_time={}, close_time={})".format(self._open_time.as_datetime(),
                                                          self._close_time.as_datetime())
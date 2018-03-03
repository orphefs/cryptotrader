from datetime import datetime


class TimeWindow(object):
    def __init__(self, start_time: datetime, end_time: datetime):
        self._start_time = start_time
        self._end_time = end_time
        self._duration = end_time - start_time

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def duration(self):
        return self._duration

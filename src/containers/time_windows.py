from datetime import datetime, timedelta


class Date(object):
    def __init__(self, date):
        self._date = date

    def as_string(self):
        return self._date.strftime('%d %b, %Y')


class TimeWindow(object):
    def __init__(self, start_time: datetime, end_time: datetime):
        self._start_time = start_time
        self._end_time = end_time
        self._duration = end_time - start_time

    @property
    def start_datetime(self):
        return self._start_time

    @property
    def end_datetime(self):
        return self._end_time

    @property
    def duration(self):
        return self._duration

    def increment_end_time_by_one_day(self):
        self._end_time += timedelta(days=1)
        return self

    def decrement_start_time_by_one_day(self):
        self._start_time -= timedelta(days=1)
        return self

    def __str__(self):
        return str(self._start_time) + str(self._end_time)

    def __is_overlap__(self, other):
        return ((other.start_datetime <= self.start_datetime < other.end_datetime) or
               (other.start_datetime < self.end_datetime <= other.end_datetime)) or \
               ((self.start_datetime <= other.start_datetime < self.end_datetime) or
               (self.start_datetime < other.end_datetime <= self.end_datetime))

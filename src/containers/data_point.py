from datetime import datetime

Price = float


class PricePoint(object):
    def __init__(self, value: Price, date_time: datetime):
        self._value = value
        self._date_time = date_time

    @property
    def value(self):
        return self._value

    @property
    def date_time(self):
        return self._date_time

    def __repr__(self):
        return "DataPoint({},{})".format(self._value, self._date_time)
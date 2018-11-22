import datetime


def datetime_to_nth_day(dt: datetime) -> int:
    nth_day = (dt - datetime.datetime(dt.year, 1, 1)).days + 1
    return nth_day


def nth_day_to_datetime(nth_day: int, year: int) -> datetime:
    dt = datetime.datetime(year, 1, 1)
    dtdelta = datetime.timedelta(days=nth_day - 1)
    return dt + dtdelta


if __name__ == '__main__':
    print(nth_day_to_datetime(365, 2018))
    print(datetime_to_nth_day(datetime.datetime(2018, 12, 31)))

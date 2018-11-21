from datetime import datetime

import pytest

from src.containers.time_windows import TimeWindow


@pytest.fixture()
def generate_time_window_1() -> TimeWindow:
    return TimeWindow(start_time=datetime(2018, 5, 1), end_time=datetime(2018, 5, 3))


@pytest.fixture()
def generate_time_window_2() -> TimeWindow:
    return TimeWindow(start_time=datetime(2018, 5, 5), end_time=datetime(2018, 5, 7))


@pytest.fixture()
def generate_time_window_3() -> TimeWindow:
    return TimeWindow(start_time=datetime(2018, 5, 2), end_time=datetime(2018, 5, 3))

@pytest.fixture()
def generate_time_window_4() -> TimeWindow:
    return TimeWindow(start_time=datetime(2018, 5, 3), end_time=datetime(2018, 5, 4))

@pytest.fixture()
def generate_time_window_5() -> TimeWindow:
    return TimeWindow(start_time=datetime(2018, 6, 2), end_time=datetime(2018, 6, 29))

@pytest.fixture()
def generate_time_window_6() -> TimeWindow:
    return TimeWindow(start_time=datetime(2018, 6, 20), end_time=datetime(2018, 6, 24))


def test_time_window():
    assert generate_time_window_1().__is_overlap__(generate_time_window_1())
    assert generate_time_window_3().__is_overlap__(generate_time_window_1())
    assert not generate_time_window_1().__is_overlap__(generate_time_window_2())
    assert not generate_time_window_2().__is_overlap__(generate_time_window_1())
    assert not generate_time_window_1().__is_overlap__(generate_time_window_4())
    assert generate_time_window_5().__is_overlap__(generate_time_window_6())

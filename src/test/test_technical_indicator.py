import os
from typing import List, Callable

import pytest

from src import definitions
from src.containers.candle import Candle
from src.live_logic.technical_indicator import TechnicalIndicator, AutoCorrelationTechnicalIndicator
from src.tools.downloader import load_from_disk


def mock_compute_callback():
    return 1.0


class MockTechnicalIndicator(TechnicalIndicator):
    def __init__(self, feature_getter_callback: Callable, lags: int):
        super(MockTechnicalIndicator, self).__init__(feature_getter_callback, lags)
        self._compute_callback = mock_compute_callback
        self._feature_getter_callback = feature_getter_callback
        self._result = None

    @property
    def result(self):
        return self._result

    def update(self, candle: Candle):
        self._candles.put(self._feature_getter_callback(candle), block=False)
        if self._candles.full():
            self._compute()
            self._candles.get(block=False)

    def _compute(self):
        self._result = self._compute_callback()


@pytest.fixture()
def load_candle_data() -> List[Candle]:
    stock_data = load_from_disk(os.path.join(definitions.DATA_DIR, "test_data.dill"))
    return stock_data.candles


def is_equal(list_1: List, list_2: List) -> bool:
    return all([item_1 == item_2 for item_1, item_2 in zip(list_1, list_2)])


def test_mock_technical_indicator():
    candles = load_candle_data()
    mti = MockTechnicalIndicator(Candle.get_close_price, lags=3)
    expected_results = [None, None, 1.0, 1.0, 1.0]
    results = []
    for candle in candles:
        mti.update(candle)
        results.append(mti.result)
    print("\nTest result is {}".format(results))
    print("Expected result is {}".format(expected_results))
    assert is_equal(results, expected_results)


def test_multiple_technical_indicators():
    candles = load_candle_data()
    ati = AutoCorrelationTechnicalIndicator(Candle.get_close_price, lags=3)
    expected_results = [None, None, 1.0, 1.0, 1.0]
    results = []
    for candle in candles:
        ati.update(candle)
        results.append(ati.result)
    print("\nTest result is {}".format(results))
    print("Expected result is {}".format(expected_results))
    assert is_equal(results, expected_results)


if __name__ == '__main__':
    # import subprocess
    #
    # # subprocess.call(['pytest', os.path.basename(__file__), '--collect-only'])
    # subprocess.call(['pytest', __file__])
    test_mock_technical_indicator()

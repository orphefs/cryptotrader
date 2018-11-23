from datetime import datetime

from src.runner import Runner
from src.type_aliases import Path


class TooManyArgumentsError(ValueError):
    pass


class runner:
    def __init__(self, trading_pair: str,
                 trade_amount: float,
                 run_type: str,
                 mock_data_start_time: datetime = None,
                 mock_data_stop_time: datetime = None,
                 path_to_stock_data: Path = None,
                 path_to_portfolio: Path = None,
                 path_to_classifier: Path = None,
                 ):
        if (mock_data_start_time and mock_data_stop_time) and path_to_stock_data:
            raise TooManyArgumentsError("Either specify start and end time OR a path to the stock data file.")

        self._runner = Runner(trading_pair, trade_amount, run_type,
                              mock_data_start_time, mock_data_stop_time,
                              path_to_stock_data, path_to_portfolio, path_to_classifier)

    def __enter__(self):
        self._runner.initialize()
        return self._runner

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self._runner.shutdown()
            traceback.print_exception(exc_type, exc_value, traceback)
            return self

    @property
    def runner(self):
        return self._runner

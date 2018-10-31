import datetime
import os

from src.containers.candle import Candle
from src.definitions import DATA_DIR
from src.mixins.save_load_mixin import DillSaveLoadMixin


class RunMetaData(DillSaveLoadMixin):
    def __init__(self, trading_pair: str = None,
                 trade_amount: float = None,
                 start_time: datetime = None,
                 stop_time: datetime = None,
                 start_candle: Candle = None,
                 stop_candle: Candle = None,
                 ):
        self._trading_pair = trading_pair
        self._trade_amount = trade_amount
        self._start_time = start_time
        self._stop_time = stop_time
        self._start_candle = start_candle
        self._stop_candle = stop_candle

    @property
    def trading_pair(self):
        return self._trading_pair

    @property
    def trade_amount(self):
        return self._trade_amount

    @property
    def start_time(self):
        return self._start_time

    @property
    def stop_time(self):
        return self._stop_time

    @property
    def start_candle(self):
        return self._start_candle

    @property
    def stop_candle(self):
        return self._stop_candle

    @trading_pair.setter
    def trading_pair(self, trading_pair: str):
        self._trading_pair = trading_pair

    @trade_amount.setter
    def trade_amount(self, trade_amount: float):
        self._trade_amount = trade_amount

    @start_time.setter
    def start_time(self, start_time: datetime):
        self._start_time = start_time

    @stop_time.setter
    def stop_time(self, stop_time):
        self._stop_time = stop_time

    @start_candle.setter
    def start_candle(self, start_candle: datetime):
        self._start_candle = start_candle

    @stop_candle.setter
    def stop_candle(self, stop_candle: datetime):
        self._stop_candle = stop_candle

    def to_csv(self):
        with open(os.path.join(DATA_DIR, "run_metadata.csv"), "w") as outfile:
            outfile.write("trading_pair:" + str(self.trading_pair) + "\n")
            outfile.write("trade_amount:" + str(self.trade_amount) + "\n")
            outfile.write("start_time:" + str(self.start_time) + "\n")
            outfile.write("stop_time:" + str(self.stop_time) + "\n")
            outfile.write("start_candle:" + str(self.start_candle) + "\n")
            outfile.write("stop_candle:" + str(self.stop_candle) + "\n")

if __name__ == '__main__':
    run_metadata = RunMetaData.load_from_disk(os.path.join(DATA_DIR, "run_metadata.dill"))
    run_metadata.to_csv()
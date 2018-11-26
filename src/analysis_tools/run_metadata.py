import argparse
import datetime
import os
from argparse import ArgumentParser

from src.containers.candle import Candle
from src.definitions import DATA_DIR
from src.mixins.save_load_mixin import DillSaveLoadMixin
from src.containers.trading_pair import TradingPair


class RunMetaData(DillSaveLoadMixin):
    def __init__(self, trading_pair: TradingPair = None,
                 trade_amount: float = None,
                 run_type: str = None,
                 start_time: datetime = None,
                 stop_time: datetime = None,
                 start_candle: Candle = None,
                 stop_candle: Candle = None,
                 ):
        self._trading_pair = trading_pair
        self._trade_amount = trade_amount
        self._run_type = run_type
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
    def run_type(self):
        return self._run_type

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
    def trading_pair(self, trading_pair: TradingPair):
        self._trading_pair = trading_pair

    @trade_amount.setter
    def trade_amount(self, trade_amount: float):
        self._trade_amount = trade_amount

    @run_type.setter
    def run_type(self, run_type: str):
        self._run_type = run_type

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

    def to_csv(self, path_to_metadata_csv: str = None):
        if path_to_metadata_csv is None:
            path_to_output = os.path.join(DATA_DIR, "run_metadata.csv")
        with open(path_to_metadata_csv, "w") as outfile:
            outfile.write("trading_pair:" + str(self.trading_pair) + "\n")
            outfile.write("trade_amount:" + str(self.trade_amount) + "\n")
            outfile.write("run_type:" + str(self.run_type) + "\n")
            outfile.write("start_time:" + str(self.start_time) + "\n")
            outfile.write("stop_time:" + str(self.stop_time) + "\n")
            outfile.write("start_candle:" + str(self.start_candle) + "\n")
            outfile.write("stop_candle:" + str(self.stop_candle) + "\n")


def main(path_to_metadata_dill: str):
    print(path_to_metadata_dill)
    run_metadata = RunMetaData.load_from_disk(path_to_metadata_dill)
    path_to_metadata_csv = os.path.join(os.path.split(path_to_metadata_dill)[0], "run_metadata.csv")
    print("Output in {}".format(path_to_metadata_csv))
    run_metadata.to_csv(path_to_metadata_csv)


class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


if __name__ == '__main__':
    parser = ArgumentParser(description="Convert metadata dill into csv")
    parser.add_argument("-i", dest="input_filename", required=False,
                        help="input .dill", action=FullPaths)
    args = parser.parse_args()
    print("Input from {}".format(args.input_filename))
    main(args.input_filename)

import logging
import os
from datetime import datetime

from src import definitions
from src.analysis_tools.run_metadata import RunMetaData
from src.definitions import DATA_DIR
from src.resource_manager import runner
from src.containers.trading_pair import TradingPair


def run_mock():
    """Replicate live run by using the information in the metadata file 
    generated by the live runner. For comparing to live run."""

    logging.basicConfig(
        filename=os.path.join(definitions.DATA_DIR, 'mock_run.log'), filemode='w',
        # stream=sys.stdout,
        level=logging.DEBUG,
    )

    run_metadata = RunMetaData.load_from_disk(os.path.join(DATA_DIR, "run_metadata.dill"))
    if run_metadata.stop_time is None:
        run_metadata.stop_time = datetime.now()

    with runner(trading_pair=TradingPair("XRP", "BTC"),
                trade_amount=100,
                run_type="mock",
                mock_data_start_time=run_metadata.start_time,
                mock_data_stop_time=run_metadata.stop_time,
                ) as lr:
        lr.run()


if __name__ == '__main__':
    run_mock()

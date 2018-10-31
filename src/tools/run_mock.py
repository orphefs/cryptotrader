import datetime

from src.run_live import runner
from src.tools.run_metadata import RunMetaData


def run_mock_replica():

    run_metadata = RunMetaData.load_from_disk("run_metadata.dill")

    with runner(trading_pair="NEOBTC",
                trade_amount=50,
                run_type="mock",
                mock_data_start_time=run_metadata.start_time,
                mock_data_stop_time=run_metadata.stop_time,
                ) as lr:
        lr.run()


if __name__ == '__main__':
    run_mock_replica()

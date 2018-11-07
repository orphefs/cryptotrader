import logging
import os

from src import definitions
from src.resource_manager import runner


def run_live():
    "Run the live algorithm with test orders (not placing real orders yet)."

    logging.basicConfig(
        filename=os.path.join(definitions.DATA_DIR, 'live_run.log'), filemode='w',
        # stream=sys.stdout,
        level=logging.DEBUG,
    )

    with runner(trading_pair="XRPBTC",
                trade_amount=100,
                run_type="live") as lr:
        lr.run()


if __name__ == '__main__':
    run_live()

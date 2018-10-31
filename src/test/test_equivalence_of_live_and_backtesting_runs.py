
import pytest

from src.live_logic.portfolio import Portfolio
from src.run_live import runner, Runner



def get_backtesting_portfolio() -> Portfolio:
    with runner("XRPBTC", 100) as lr:
        lr.run_backtesting_batch()
        # portfolio = lr.portfolio

    return portfolio


def get_mock_live_run_portfolio() -> Portfolio:
    lr = Runner(trading_pair="XRPBTC",
                trade_amount=100)
    lr.initialize()
    lr.mock_run_live()
    lr.shutdown()
    # portfolio = lr.portfolio

    return portfolio


def test_equivalence_of_live_and_backtesting_runs():
    mock_live_portfolio = get_mock_live_run_portfolio()
    # backtesting_portfolio = get_backtesting_portfolio()
    assert mock_live_portfolio.positions_df == backtesting_portfolio.positions_df


if __name__ == '__main__':
    import subprocess

    # subprocess.call(['pytest', os.path.basename(__file__), '--collect-only'])
    subprocess.call(['pytest', __file__])
    # pass

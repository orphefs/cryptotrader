import os
from datetime import timedelta
import logging
import time

from binance.client import Client
from sklearn.ensemble import RandomForestClassifier

import definitions
from containers.trade_helper import generate_trading_signal_from_prediction
from live_logic.parameters import LiveParameters
from live_logic.portfolio import Portfolio
from tools.downloader import download_live_data
from tools.train_classifier import TradingClassifier

logging.basicConfig(filename=os.path.join(definitions.DATA_DIR, 'local_autotrader.log'), level=logging.INFO)


def get_capital_from_account(capital_security: str) -> float:
    return 5.0


def run(trade_amount: float, capital_security: str, trading_pair: str):
    client = Client("", "")
    parameters = LiveParameters(
        update_period=timedelta(hours=1),
        trade_amount=1000,
        sleep_time=0
    )
    portfolio = Portfolio(initial_capital=get_capital_from_account(capital_security=None),
                          trade_amount=parameters.trade_amount)

    training_ratio = 0.5  # this is not enabled

    classifier = TradingClassifier.load_from_disk(os.path.join(definitions.DATA_DIR, "classifier.dill"))

    logging.info("Initialized portfolio: {}".format(portfolio))

    while True:
        candle = download_live_data(client, security=trading_pair, )
        classifier.append_new_candle(candle)
        prediction = classifier.predict_one(candle)
        if prediction is not None:
            signal = generate_trading_signal_from_prediction(prediction[0], candle)
            portfolio.update(signal)
            portfolio.save_to_disk(os.path.join(definitions.DATA_DIR, "portfolio.dill"))
        time.sleep(parameters.sleep_time)

    portfolio.compute_performance()
    custom_plot(portfolio, strategy, parameters, stock_data)
    print(portfolio._point_stats['base_index_pct_change'])
    print(portfolio._point_stats['total_pct_change'])

    plt.show()


if __name__ == '__main__':
    run(trade_amount=1000, capital_security="BTC", trading_pair="XRP")

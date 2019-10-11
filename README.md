**CryptoTrader**

This project implements an automated trading bot, which makes predictions on market movements, buys and sells cryptocurrency (or stocks) automatically, based on historical market data.

The 

*Disclaimer: This is for educational purposes only and Orfeas Kypris does not bear any responsibility for any financial losses, or otherwise,  incurred due to misuse of this code. Please use responsibly and at your own risk.*

---

## Training the algorithm

You’ll start by training the algorithm using historical trading data. The code contains interfaces for two trading platforms, [Binance](http://www.binance.com) and [Cobinhood](http://www.cobinhood.com). 

To start, from the root folder (cryptotrader), run:
*PYTHONPATH=. python3 src/classification/train_classifier.py*

This will do the following:

1. Download stock data based on the configuration you provide it within the *train_classifier.py* file. Parameters are 1) time window (i.e. 19 Sep 2019 to 21 Sep 2019), 2) time interval (i.e. 1 min / 1 hour), 3) trading pair (i.e. ETHBTC).
2. Train the model using a random forest classifier fed with some custom extracted features of the time series, such as RSI, movnig average etc. The features are configurable through an abstract interface (for the brave).

## Running the algorithm

The algorithm can be run in three main modes: offline, mock live, and live. 

**Live** mode will place real orders, and requires an API key for the selected platform. If no API key is provided, the algorithm will place mock orders, which is recommended in the beggining.

**Offline** is recommended for debugging purposes and for getting quick results (for the impatient), which can then be readily analyzed, to evaluate trading strategy performance using various metrics. The disadvantage of this mode is that results are not representative of live trading, as slippage effects are not taking into account.

**Mock live** is used for troubleshooting purposes. It collects data from the live run, and replicates the live run by downloading the candles used in the live run as historical data and running the predictions on those. This can be useful for troubleshooting since sometimes exchanges may distort their historical data (on purpose?). Same disadvantages as with the offline mode holds. 

All of the above modes save a log and trading performance data for further analysis.

---

## Postprocessing

Coming soon...
---


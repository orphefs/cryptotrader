**CryptoTrader**

This project implements an automated trading bot, which makes predictions on market movements, buys and sells cryptocurrency (or stocks) automatically, based on historical market data.

*Disclaimer: The project is experimental and still under development.*

*Disclaimer: This is for educational purposes only and Orfeas Kypris does not bear any responsibility for any financial losses, or otherwise,  incurred due to misuse of this code. Please use responsibly and at your own risk.*

---

## Installation

The code runs on Python 3.7. To install dependencies, run *pip install -r requirements.txt*.

## Training the algorithm

You’ll start by training the algorithm using historical trading data. The code contains interfaces for two trading platforms, [Binance](http://www.binance.com) and [Cobinhood](http://www.cobinhood.com). 

To start, from the root folder (cryptotrader), run:
*PYTHONPATH=. python3 src/classification/train_classifier.py*

This will do the following:

1. Download stock data based on the configuration you provide it within the *train_classifier.py* file. Parameters are 1) time window (i.e. 19 Sep 2019 to 21 Sep 2019), 2) time interval (i.e. 1 min / 1 hour), 3) trading pair (i.e. ETHBTC). A typical filename where the stock data is saved is *local_data_19_Sep,_2019_20_Sep,_2019_XRPBTC_0:01:00_<class_'binance.client.Client'>.dill*
2. Train the model using a random forest classifier fed with some custom extracted features of the time series, such as RSI, movnig average etc. The features are configurable through an abstract interface (for the brave).
3. Serialize the trained model onto classifier.dill file and save it in the $PROJECT_ROOT/data directory	.

## Running the algorithm

The algorithm can be run in three main modes: offline, mock live, and live. 

**Live** mode will place real orders, and requires an API key for the selected platform. The algorithm can be configured to place mock orders (Cobinhood exchange offers this feature), which is recommended in the beggining, to avoid implementing a wrong trading strategy. A typical *live_run.log* looks like that:

```
DEBUG:cobinhood-api:cobinhood_api.http.chart fetch "get_candles"
INFO:root:Registering candle: Candle(Price(open_price=0.027499, high_price=0.027499, low_price=0.027499, close_price=0.027499 ),
Volume(volume=0.0, taker_buy_base_asset_volume=nan, taker_buy_quote_asset_volume=nan, quote_asset_volume=nan, number_of_trades=nan,  ),
Time(open_time=None, close_time=2019-09-07 23:51:00))
INFO:root:Prediction is: [ 1.] on iteration 0
INFO:root:Prediction for signal SignalSell(1.0 at DataPoint(0.027499,2019-09-07 23:51:00))
DEBUG:cobinhood-api:cobinhood_api.http.trading fetch "get_orders"
INFO:root:Previous signal was SignalBuy...
INFO:root:Current signal is SignalSell...
INFO:root:Last filled order is NoneType...
INFO:root:Open order is NoneType...
DEBUG:cobinhood-api:cobinhood_api.http.trading fetch "get_order_history"
INFO:root:Fetched last filled order...
INFO:root:Current signal is SignalSell and last filled order is OrderSell...
INFO:root:Doing nothing...
```

If an API key is not given, the client will not connect to the trading platform, and thus won't be able to fetch order information. A typical such error message is the following:
`__main__.CobinhoodError: Could not fetch last n orders. Reason: cache_key_not_exists`

**Offline** is recommended for debugging purposes and for getting quick results (for the impatient), which can then be readily analyzed, to evaluate trading strategy performance using various metrics. The disadvantage of this mode is that results are not representative of live trading, as slippage effects are not taking into account.

**Mock live** is used for troubleshooting purposes. It collects data from the live run, and replicates the live run by downloading the candles used in the live run as historical data and running the predictions on those. This can be useful for troubleshooting since sometimes exchanges may distort their historical data (on purpose?). Same disadvantages as with the offline mode holds. 

All of the above modes save a log and trading performance data for further analysis.

---

## Postprocessing

Coming soon...

---


from datetime import timedelta

from src.type_aliases import BinanceClient

binance_sampling_rate_mappings = {
    timedelta(minutes=1).total_seconds(): BinanceClient.KLINE_INTERVAL_1MINUTE,
    timedelta(minutes=3).total_seconds(): BinanceClient.KLINE_INTERVAL_3MINUTE,
    timedelta(minutes=5).total_seconds(): BinanceClient.KLINE_INTERVAL_5MINUTE,
    timedelta(minutes=15).total_seconds(): BinanceClient.KLINE_INTERVAL_15MINUTE,
    timedelta(minutes=30).total_seconds(): BinanceClient.KLINE_INTERVAL_30MINUTE,
    timedelta(hours=1).total_seconds(): BinanceClient.KLINE_INTERVAL_1HOUR,
    timedelta(hours=2).total_seconds(): BinanceClient.KLINE_INTERVAL_2HOUR,
    timedelta(hours=4).total_seconds(): BinanceClient.KLINE_INTERVAL_4HOUR,
    timedelta(hours=6).total_seconds(): BinanceClient.KLINE_INTERVAL_6HOUR,
    timedelta(hours=8).total_seconds(): BinanceClient.KLINE_INTERVAL_8HOUR,
    timedelta(hours=12).total_seconds(): BinanceClient.KLINE_INTERVAL_12HOUR,
    timedelta(days=1).total_seconds(): BinanceClient.KLINE_INTERVAL_1DAY,
    timedelta(days=3).total_seconds(): BinanceClient.KLINE_INTERVAL_3DAY,
    timedelta(days=7).total_seconds(): BinanceClient.KLINE_INTERVAL_1WEEK,
    timedelta(days=30).total_seconds(): BinanceClient.KLINE_INTERVAL_1MONTH,
}
cobinhood_sampling_rate_mappings = {
    timedelta(minutes=1).total_seconds(): "1m",
    timedelta(minutes=5).total_seconds(): "5m",
    timedelta(minutes=15).total_seconds(): "15m",
    timedelta(minutes=30).total_seconds(): "30m",
    timedelta(hours=1).total_seconds(): "1h",
    timedelta(hours=6).total_seconds(): "6h",
    timedelta(hours=12).total_seconds(): "12h",
}
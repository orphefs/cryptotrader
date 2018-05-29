import os

from binance.client import Client

from helpers import convert_to_timedelta

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')  # This is your Project Root
CONFIG_PATH = os.path.join(ROOT_DIR, 'src', 'config', 'onoff.txt')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
TEST_DATA_DIR = os.path.join(ROOT_DIR, 'src','test', 'data')
update_interval_mappings = {
    Client.KLINE_INTERVAL_1MINUTE: convert_to_timedelta(Client.KLINE_INTERVAL_1MINUTE),
    Client.KLINE_INTERVAL_3MINUTE: convert_to_timedelta(Client.KLINE_INTERVAL_3MINUTE),
    Client.KLINE_INTERVAL_5MINUTE: convert_to_timedelta(Client.KLINE_INTERVAL_5MINUTE),
    Client.KLINE_INTERVAL_15MINUTE: convert_to_timedelta(Client.KLINE_INTERVAL_15MINUTE),
    Client.KLINE_INTERVAL_30MINUTE: convert_to_timedelta(Client.KLINE_INTERVAL_30MINUTE),
    Client.KLINE_INTERVAL_1HOUR: convert_to_timedelta(Client.KLINE_INTERVAL_1HOUR),
    Client.KLINE_INTERVAL_2HOUR: convert_to_timedelta(Client.KLINE_INTERVAL_2HOUR),
    Client.KLINE_INTERVAL_4HOUR: convert_to_timedelta(Client.KLINE_INTERVAL_4HOUR),
    Client.KLINE_INTERVAL_6HOUR: convert_to_timedelta(Client.KLINE_INTERVAL_6HOUR),
    Client.KLINE_INTERVAL_8HOUR: convert_to_timedelta(Client.KLINE_INTERVAL_8HOUR),
    Client.KLINE_INTERVAL_12HOUR: convert_to_timedelta(Client.KLINE_INTERVAL_12HOUR),
    Client.KLINE_INTERVAL_1DAY: convert_to_timedelta(Client.KLINE_INTERVAL_1DAY),
    Client.KLINE_INTERVAL_3DAY: convert_to_timedelta(Client.KLINE_INTERVAL_3DAY),
    Client.KLINE_INTERVAL_1WEEK: convert_to_timedelta(Client.KLINE_INTERVAL_1WEEK),
    Client.KLINE_INTERVAL_1MONTH: convert_to_timedelta(Client.KLINE_INTERVAL_1MONTH),
}
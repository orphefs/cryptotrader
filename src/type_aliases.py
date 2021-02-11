from enum import Enum

from binance.client import Client

Seconds = float

Path = str
Hash = str
BinanceOrder = dict

BinanceClient = Client

class Exchange(Enum):
    BINANCE = 1


from enum import Enum

Seconds = float

Path = str
Hash = str
BinanceOrder = dict


class Exchange(Enum):
    BINANCE = 1
    COBINHOOD = 2

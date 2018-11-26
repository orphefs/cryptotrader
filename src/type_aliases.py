from enum import Enum

Seconds = float
Security = str
Path = str
Hash = str
BinanceOrder = dict


class Exchange(Enum):
    BINANCE = 1
    COBINHOOD = 2

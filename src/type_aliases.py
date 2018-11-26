from enum import Enum

from binance.client import Client
from cobinhood_api import Cobinhood

Seconds = float

Path = str
Hash = str
BinanceOrder = dict

BinanceClient = Client
CobinhoodClient = Cobinhood

class Exchange(Enum):
    BINANCE = 1
    COBINHOOD = 2

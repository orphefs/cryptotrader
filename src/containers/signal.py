from src.containers.data_point import PricePoint


class _TradingSignal(object):
    def __init__(self, signal: int, price_point: PricePoint):
        '''
        Container class.
        Parameters
        ----------
        signal: The type of action (Buy, Sell, Hold) that needs to be taken at a specific timestamp in order for the action to be valid.
        price_point: A PricePoint object containing the timestamp and price of a trading pair at that timestamp.
        '''

        self.signal = signal
        self.type = _signal_types[signal]
        self.price_point = price_point

    def __repr__(self):
        return type(self).__name__ + "({} at {})".format(self.signal, self.price_point)

    def __str__(self):
        return type(self).__name__

    @staticmethod
    def from_integer_value(integer_value: int, price_point: PricePoint):
        cls = _signal_types[integer_value]
        return cls(integer_value, price_point)

    def __eq__(self, other):
        return (self.signal == other.signal) and \
               (self.type == other.type) and \
               (self.price_point == other.price_point)

    def as_dict(self):
        return {"type": str(self),
                "price_point": self.price_point.as_dict()
                }


def generate_trading_signal(*args, **kwargs):
    if len(args) == 0 and len(kwargs) == 0:
        return _TradingSignal
    else:
        return _TradingSignal(*args, **kwargs)


class SignalBuy(_TradingSignal):
    pass


class SignalSell(_TradingSignal):
    pass


class SignalHold(_TradingSignal):
    pass


_signal_types = {-1: SignalBuy,
                 1: SignalSell,
                 0: SignalHold, }

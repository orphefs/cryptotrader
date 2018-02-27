from abc import ABC, abstractmethod

from containers.time import Time

Price = float
Instrument = str


class Order(ABC):
    pass


class MarketOrder(Order):
    def __init__(self, place_time: Time, execution_time: Time, execution_price: Price, instrument: Instrument):
        self._place_time = place_time
        self._execution_time = execution_time
        self._execution_price = execution_price
        self._instrument = instrument

    @property
    def place_time(self):
        return self._place_time

    @property
    def execution_time(self):
        return self._execution_time

    @property
    def execution_price(self):
        return self._execution_price

    @property
    def instrument(self):
        return self._instrument


class BuyOrder(MarketOrder):
    def __init__(self, place_time: Time, execution_time: Time, execution_price: Price, instrument: Instrument):
        super(BuyOrder).__init__(place_time, execution_time, execution_price, instrument)

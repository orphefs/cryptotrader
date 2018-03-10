from typing import Callable


class Event:
    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    def get_handler_count(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__ = get_handler_count


def download_data(client: BinanceClient):
    pass


def update_moving_average(new_data: Data, processed_stock_data: ProcessedStockData):
    pass


def buy_sell_x_amount(processed_stock_data: ProcessedStockData, strategy: Strategy):
    pass


def update_portfolio(portfolio: Portfolio):
    pass


def calculate_performance(portfolio: Portfolio)
    pass


class AutoTrader:
    def __init__(self):
        self.newDataAvailable = Event()
        self.movingAverageUpdated = Event()
        self.orderPlaced = Event()
        self.portfolioUpdated = Event()
        self.portfolio = Portfolio()
        self.stock_data = StockData()
        self.processed_stock_data = ProcessedStockData()

    def add_handlers(self):
        self.newDataAvailable += update_moving_average
        self.movingAverageUpdated += buy_sell_x_amount
        self.orderPlaced += update_portfolio
        self.portfolioUpdated += calculate_performance

    def trade(self):
        data = download_data()
        self.newDataAvailable(data)
        self.movingAverageUpdated()
        self.orderPlaced()
        self.portfolioUpdated()



class Subscriber:
    def __init__(self, name):
        self.name = name

    def update(self, message):
        print('{} got message "{}"'.format(self.name, message))


class Publisher:
    def __init__(self, events):
        # maps event names to subscribers
        # str -> dict
        self.events = {event: dict()
                       for event in events}

    def get_subscribers(self, event):
        return self.events[event]

    def register(self, event, who, callback=None):
        if callback == None:
            callback = getattr(who, 'update')
        self.get_subscribers(event)[who] = callback

    def unregister(self, event, who):
        del self.get_subscribers(event)[who]

    def dispatch(self, event, message):
        for subscriber, callback in self.get_subscribers(event).items():
            callback(message)

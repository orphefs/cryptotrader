import socketio
import _thread

from src.client.restartable_thread import RestartableThread
from src.client.thread import NormalThread
from src.containers.trading_pair import TradingPair

sio = socketio.Client()


@sio.event
def connect():
    sio.emit("clientId", "cryptotrader")
    print('connection established')
    _thread.start_new_thread(run, (), {"socket_io": sio})


@sio.event
def my_message(data):
    print('message received with ', data)
    # sio.emit('my response', {'response': 'my response'})


@sio.event
def disconnect():
    print('disconnected from server')


def run(*args, **kwargs):
    # TODO: pass trading_pairs as argument (list)
    trading_pairs = [
        # TradingPair("XRP", "ETH"),
        TradingPair("XRP", "BTC"),
        TradingPair("ETH", "BTC"),
        # TradingPair("ZIL", "BTC"),
        # TradingPair("ADA", "ETH"),
        TradingPair("ADA", "BTC"),
    ]
    cryptotrader_threads = []
    for trading_pair in trading_pairs:
        cryptotrader_thread = RestartableThread(trading_pair=trading_pair,
            websocket_client=kwargs["socket_io"])
        cryptotrader_threads.append(cryptotrader_thread)

    # TODO: use logging.log to output on stdout from each thread
    for cryptotrader_thread in cryptotrader_threads:
        NormalThread(cryptotrader_thread).start()


if __name__ == '__main__':
    # TODO: implement resource manager?
    sio.connect('http://localhost:4001')
    sio.wait()

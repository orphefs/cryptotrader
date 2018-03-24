from queue import Queue
import numpy as np


class RollingMean:
    def __init__(self, window_size: int):
        self._window_size = float(window_size)
        self._data = Queue(maxsize=window_size)
        self._new_sample = float
        self._old_sample = float
        self._mode = str
        self._new_mean = float

    @property
    def mean(self):
        return self._new_mean

    def insert_new_sample(self, sample: float):
        self._new_sample = sample
        if self._data.qsize() < self._data.maxsize:
            self._mode = 'cumulative'
            self._data.put(sample, block=False)
            print(self._data.qsize())
        else:
            self._mode = 'rolling'
            self._old_sample = self._data.get()
            self._data.put(sample, block=False)
            print(self._data.qsize())
        self._update_state()

    def _select_mode(self):
        if self._data.full():
            self._mode = 'rolling'
        else:
            self._mode = 'cumulative'
            print(self._mode)

    def _compute_mean(self):
        self._new_mean = np.mean(list(self._data.queue))
        self._old_mean = self._new_mean

    def _update_state(self):
        if self._mode == 'cumulative':
            self._compute_mean()
        elif self._mode == 'rolling':
            self._new_mean = self._old_mean + (self._new_sample / self._window_size) - (
                self._old_sample / self._window_size)
        else:
            pass

        self._old_mean = self._new_mean


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    rm = RollingMean(10)
    raw_data = np.arange(0,100) + np.random.normal(0,20,100)
    means = []
    for item in raw_data:
        rm.insert_new_sample(item)
        print(rm.mean)
        means.append(rm.mean)
    plt.plot(raw_data)
    plt.plot(means)
    plt.show()
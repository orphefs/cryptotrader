# Importing the modules
import threading
import sys

# Custom Thread Class
import time


class MyException(Exception):
    pass


class MyThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs
        super().__init__(*args, **kwargs)

    def clone(self):
        return MyThread(*self._args, **self._kwargs)

    def someFunction(self):
        time.sleep(1.0)
        raise Exception("Hi, I am an exception in thread {}!".format(threading.current_thread().name))


    def run(self):
        self.exc = None
        try:
            self.someFunction()
        except BaseException as e:
            self.exc = e

    def join(self):
        threading.Thread.join(self)

        if self.exc:
            raise self.exc

    # Driver function


def main():
    t = MyThread()

    while True:
        t.start()
        try:
            t.join()
        except Exception as e:
            print("Exception handled in Main,details of the exception: {}".format(e))
            t = t.clone()
        time.sleep(1.0)

# Driver code
if __name__ == '__main__':
    main()

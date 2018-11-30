from typing import Callable


def print_function_name(func: Callable):
    def func_wrapper(*args, **kwargs):
        print("Running function {}\n".format(func.__name__))
        return func(*args, **kwargs)

    return func_wrapper

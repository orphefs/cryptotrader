import logging
import time
from typing import Callable

import requests


class NetworkError(RuntimeError):
    pass


def retry_on_network_error(func: Callable):
    retry_on_exceptions = (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError
    )
    max_retries = 3600
    timeout = 2

    def inner(*args, **kwargs):
        for i in range(max_retries):
            try:
                result = func(*args, **kwargs)
            except retry_on_exceptions:
                time.sleep(timeout)
                logging.debug("Connection error. Retrying")
                continue
            else:
                return result
        else:
            raise NetworkError

    return inner

import logging


class LoggingFilter(logging.Filter):
    def __init__(self, log_level):
        super(LoggingFilter, self).__init__()
        self.log_level = log_level

    def filter(self, rec):
        return rec.levelno == self.log_level

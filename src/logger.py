import logging

import coloredlogs

logger = logging.getLogger('cryptotrader-api')
coloredlogs.install(level='DEBUG', logger=logger)

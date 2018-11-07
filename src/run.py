import logging
import os

from src import definitions

logging.basicConfig(
    filename=os.path.join(definitions.DATA_DIR, 'local_autotrader.log'), filemode='w',
    # stream=sys.stdout,
    level=logging.DEBUG,
)
logger = logging.getLogger('cryptotrader_api')

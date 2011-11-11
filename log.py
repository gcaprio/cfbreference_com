import logging
import logging.handlers
from env_vars import *

if not hasattr(logging, "set_up_done"):
    logging.set_up_done = False

def init_logging(LOGGING_DIR):
    if logging.set_up_done:
        return

    LOG_FILENAME = os.path.join(LOGGING_DIR, 'cfbreference.com.log').replace('\\', '/')

    logging.basicConfig(level=logging.DEBUG)

    rotatingFileHandler = logging.handlers.TimedRotatingFileHandler(filename=LOG_FILENAME, when='midnight')
    rotatingFileHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    rotatingFileHandler.setFormatter(formatter)
    logging.getLogger().addHandler(rotatingFileHandler)

    logging.set_up_done = True

"""Global application logger

Initially the logger is a no-op.
It will be replaced by a real logger during application initialization.
"""

import logging
import sys


_LOGGER_NAME = "trappedbot"


def _init_logger():
    """Initialize the application logger

    This is intended to be called just once internally.
    After startup, just configure this module's LOGGER directly.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    formatter = logging.Formatter("%(asctime)s | %(name)s [%(levelname)s] %(message)s")
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


LOGGER = _init_logger()

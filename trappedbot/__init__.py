"""Trapped in a Matrix server, send help!"""

import logging
from importlib.metadata import version


LOGGER = logging.getLogger(__name__)

HELP_TRAPPED_MSG = "Trapped in a Matrix server, send help!"


def version_raw() -> str:
    return version("trappedbot")


def version_cute() -> str:
    return f"{HELP_TRAPPED_MSG} Version {version_raw()}"

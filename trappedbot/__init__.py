"""Trapped in a Matrix server, send help!"""

import logging
from importlib.metadata import version

from trappedbot.config import AppConfig


# Default, no-op logger and configuration
# These will be replaced by real values during appliation initialization
LOGGER = logging.getLogger(__name__)
APPCONFIG = AppConfig()

HELP_TRAPPED_MSG = "Trapped in a Matrix server, send help!"


def version_raw() -> str:
    """Return the raw package version"""
    return version("trappedbot")


def version_cute() -> str:
    """Return a package version string aligned with our brand"""
    return f"{HELP_TRAPPED_MSG} Version {version_raw()}"

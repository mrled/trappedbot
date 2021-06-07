"""Global application configuration.

The global application configuration is safe to retrieve with `get()` at any time,
even immediately after the application starts;
if the config file has not been read in, it will just return empty/dummy values.
"""

import typing

from trappedbot.configuration import Configuration


# This internal variable should not be used directly,
# as it may be None depending on when it is referenced.
_APPCONFIG: typing.Optional[Configuration] = None


def get() -> Configuration:
    """Retrieve the global application configuration"""
    global _APPCONFIG
    return _APPCONFIG or Configuration()


def set(conf: Configuration) -> None:
    """Set the global application configuration"""
    global _APPCONFIG
    _APPCONFIG = conf

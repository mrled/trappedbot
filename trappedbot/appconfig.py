"""Global application configuration

Initially the _APPCONFIG variable is full of empty, dummy values;
it will be replaced by real values during application initialization.

Note that consumers should use the get() and set() methods, NOT the _APPCONFIG
global, in order to avoid circular imports.
"""

import typing

from trappedbot.configuration import Configuration


_APPCONFIG: typing.Optional[Configuration] = None


def get() -> Configuration:
    global _APPCONFIG
    return _APPCONFIG or Configuration()


def set(conf: Configuration) -> None:
    global _APPCONFIG
    _APPCONFIG = conf

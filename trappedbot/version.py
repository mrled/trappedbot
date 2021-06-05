"""Application version information"""

from importlib.metadata import version

from trappedbot.constants import HELP_TRAPPED_MSG


def version_raw() -> str:
    """Return the raw package version"""
    return version("trappedbot")


def version_cute() -> str:
    """Return a package version string aligned with our brand"""
    return f"{HELP_TRAPPED_MSG} Version {version_raw()}"
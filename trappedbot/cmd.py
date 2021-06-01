#!/usr/bin/env python

import argparse
import asyncio
import logging
import os
import sys
import traceback
import typing

import trappedbot
from trappedbot import util

from trappedbot.botclient import botloop


def ExistingResolvedPath(path):
    if os.path.exists(path):
        return os.path.abspath(path)
    else:
        raise FileNotFoundError(f"Path {path} does not exist")


def parseargs(arguments: typing.List[str]) -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description=trappedbot.HELP_TRAPPED_MSG,
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Include verbose/debug messages, and enter the debugger on unhandled exceptions",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Include verbose/debug messages"
    )

    subparsers = parser.add_subparsers(dest="action")
    subparsers.required = True

    # sub_version =
    subparsers.add_parser("version", help="Show version")

    sub_bot = subparsers.add_parser("bot", help="Start the bot")
    sub_bot.add_argument(
        "configpath", type=ExistingResolvedPath, help="Path to the config file"
    )

    return parser.parse_args(arguments)


def main(arguments: typing.List[str] = sys.argv[1:]):
    """The command-line main function"""

    parsed = parseargs(arguments)

    if parsed.verbose:
        trappedbot.LOGGER.setLevel(logging.DEBUG)
    if parsed.debug:
        sys.excepthook = util.idb_excepthook
        trappedbot.LOGGER.setLevel(logging.DEBUG)

    if parsed.action == "version":
        print(trappedbot.version_cute())
        sys.exit(0)

    elif parsed.action == "bot":
        try:
            asyncio.get_event_loop().run_until_complete(botloop(parsed.configpath))
        except KeyboardInterrupt:
            trappedbot.LOGGER.debug("Received keyboard interrupt, exiting...")
            sys.exit(0)
        except Exception as exc:
            trappedbot.LOGGER.error(
                f"Encountered exception: {exc}\nTraceback:\n{traceback.format_exc()}"
            )
            sys.exit(1)

    else:
        raise Exception(f"Unknown action {parsed.action}")

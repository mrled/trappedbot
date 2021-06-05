#!/usr/bin/env python

import argparse
import asyncio
import getpass
import logging
import os
import sys
import traceback
import typing

import requests

from trappedbot import appconfig, util
from trappedbot.applogger import LOGGER
from trappedbot.botclient import botloop
from trappedbot.configuration import parse_config
from trappedbot.constants import HELP_TRAPPED_MSG
from trappedbot.tasks.builtin import BUILTIN_TASKS
from trappedbot.version import version_cute


def ExistingResolvedPath(path):
    if os.path.exists(path):
        return os.path.abspath(path)
    else:
        raise FileNotFoundError(f"Path {path} does not exist")


def access_token(
    homeserver: str, user: str, password: str, deviceid: str, devicename: str
) -> str:
    """Retrieve a bearer token from a Matrix homeserver"""
    data = {
        "identifier": {
            "type": "m.id.user",
            "user": user,
        },
        "password": password,
        "type": "m.login.password",
        "device_id": deviceid,
        "initial_device_display_name": devicename,
    }
    uri = f"{homeserver}/_matrix/client/r0/login"

    result = requests.post(uri, json=data)
    # A successful request will return something like this:
    # '{"user_id":"@me:micahrl.com","access_token":"...ELIDED...","home_server":"micahrl.com","device_id":"ifrit_get_mx_users","well_known":{"m.homeserver":{"base_url":"https://matrix.micahrl.com/"}}}'
    # In case the request was not successful, raise an error
    result.raise_for_status()
    jresult = result.json()
    return jresult["access_token"]


def parseargs(arguments: typing.List[str]) -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description=HELP_TRAPPED_MSG,
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

    # sub_builtins =
    subparsers.add_parser("builtin-tasks", help="List built in tasks")

    sub_acctok = subparsers.add_parser(
        "access-token", help="Get an access token from a Matrix server"
    )
    sub_acctok.add_argument(
        "homeserver",
        help="The matrix homeserver to use, like 'https://matrix.example.com'",
    )
    sub_acctok.add_argument(
        "username",
        help="The username to retrieve a token for. Just the name, not a full mxid. You will be prompted for a password.",
    )
    sub_acctok.add_argument(
        "deviceid",
        help="A device ID to use. Arbitrary, but helpful in identifying the purpose of an access token later.",
    )
    sub_acctok.add_argument(
        "--devicename", help="A human-readable device name; defaults to the device ID"
    )
    sub_acctok.add_argument(
        "--password",
        help="Password for the account. Will be prompted for this if not passed.",
    )

    return parser.parse_args(arguments)


def main(arguments: typing.List[str] = sys.argv[1:]):
    """The command-line main function"""

    parsed = parseargs(arguments)

    # force_log_debug is an not beautiful and a bit repetitive, but it lets me
    # ensure that the command line flags can override settings in the config
    # file if used, and the logger gets set up properly if it wasn't.
    force_log_debug = False
    if parsed.verbose or parsed.debug:
        LOGGER.setLevel(logging.DEBUG)
        force_log_debug = True
    if parsed.debug:
        sys.excepthook = util.idb_excepthook

    if parsed.action == "version":
        print(version_cute())
        sys.exit(0)

    elif parsed.action == "bot":
        appconfig.set(parse_config(parsed.configpath, force_log_debug))
        try:
            asyncio.get_event_loop().run_until_complete(botloop())
        except KeyboardInterrupt:
            LOGGER.debug("Received keyboard interrupt, exiting...")
            sys.exit(0)
        except Exception as exc:
            LOGGER.error(
                f"Encountered exception: {exc}\nTraceback:\n{traceback.format_exc()}"
            )
            sys.exit(1)

    elif parsed.action == "builtin-tasks":
        print("The following tasks are built-in to the bot:")
        for k, v in BUILTIN_TASKS.items():
            print(f"- {k}")

    elif parsed.action == "access-token":
        password = parsed.password or getpass.getpass()
        devicename = parsed.devicename or parsed.deviceid
        token = access_token(
            parsed.homeserver, parsed.username, password, parsed.deviceid, devicename
        )
        print(token)

    else:
        raise Exception(f"Unknown action {parsed.action}")

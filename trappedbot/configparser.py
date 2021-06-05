import json
import logging
import os
import re
import typing

import yaml

from trappedbot.applogger import LOGGER
from trappedbot.commands.builtin import BUILTIN_COMMANDS
from trappedbot.commands.command_list import yamlobj2cmddict
from trappedbot.configuration import ConfigError, Configuration
from trappedbot.responses.response_list import yamlobj2rsplist


def parse_config(
    filepath: str,
    force_log_debug: bool = False,
) -> Configuration:
    """Parse a config file

    Return a tuple of an AppConfig object and a Logger
    """
    filepath = os.path.abspath(filepath)
    if not os.path.isfile(filepath):
        raise ConfigError(f"Config file '{filepath}' does not exist")

    with open(filepath) as f:
        configuration = yaml.safe_load(f.read())

    # Logging setup
    if force_log_debug:
        LOGGER.setLevel(logging.DEBUG)
    elif (config_log_lvl := configuration["logging"].get("level", None)) :
        LOGGER.setLevel(config_log_lvl)

    database_filepath = os.path.abspath(configuration["storage"]["database_filepath"])
    store_filepath = os.path.abspath(configuration["storage"]["store_filepath"])
    os.makedirs(store_filepath, exist_ok=True)
    os.makedirs(os.path.dirname(database_filepath), exist_ok=True)

    user_id = configuration["matrix"]["user_id"]
    if not re.match("@.*:.*", user_id):
        raise ConfigError("matrix.user_id must be in the form @name:domain")

    # Retrieve the access credential. Prefer the access token if both are present.
    user_password = configuration["matrix"].get("user_password", None)
    user_access_token = configuration["matrix"].get("access_token", None)
    if not user_password and not user_access_token:
        raise ConfigError("Either user_password or access_token must be specified")

    device_id = configuration["matrix"]["device_id"]
    device_name = configuration["matrix"]["device_name"]
    homeserver_url = configuration["matrix"]["homeserver_url"]
    trust_own_devices = configuration["matrix"]["trust_own_devices"]
    change_device_name = configuration["matrix"]["change_device_name"]

    command_prefix = configuration["bot"]["command_prefix"]
    trusted_users = configuration["bot"].get("trusted_users", [])

    commands = yamlobj2cmddict(configuration.get("commands", {}))
    for cmdname, cmd in BUILTIN_COMMANDS.items():
        if cmdname in commands:
            LOGGER.warning(
                f"A user-defined command '{cmdname}' conflicts with a built-in command of the same name. Overriding the user-defined command with the builtin."
            )
        commands[cmdname] = cmd
    responses = yamlobj2rsplist(configuration.get("responses", []))

    appconfig = Configuration(
        configuration=configuration,
        config_filepath=filepath,
        database_filepath=database_filepath,
        store_filepath=store_filepath,
        user_id=user_id,
        user_password=user_password,
        user_access_token=user_access_token,
        device_id=device_id,
        device_name=device_name,
        homeserver_url=homeserver_url,
        trust_own_devices=trust_own_devices,
        change_device_name=change_device_name,
        command_prefix=command_prefix,
        trusted_users=trusted_users,
        commands=commands,
        responses=responses,
    )

    return appconfig

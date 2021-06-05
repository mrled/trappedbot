#!/usr/bin/env python3

"""Implement utility functions for

- reading in the YAML config file
- performing the according initialization and set-up
"""

import json
import logging
import os
import re
from trappedbot.commands.builtin import BUILTIN_COMMANDS
import typing

import yaml

from trappedbot.applogger import LOGGER
from trappedbot.commands.command_list import CommandList
from trappedbot.responses.response_list import ResponseList


class Configuration(typing.NamedTuple):
    """Application configuration"""

    configuration: typing.Dict = {}
    config_filepath: str = ""
    database_filepath: str = ""
    store_filepath: str = ""
    task_dict_filepath: str = ""
    user_id: str = ""
    user_password: str = ""
    user_access_token: str = ""
    device_id: str = ""
    device_name: str = ""
    homeserver_url: str = ""
    trust_own_devices: bool = False
    change_device_name: bool = False
    command_prefix: str = ""
    trusted_users: typing.List[str] = []
    commands: CommandList = CommandList({})
    responses: ResponseList = ResponseList([])

    def extension(self, section: str, setting: str):
        """Retrieve an extension from the config

        Allows users to store any setting in our app config and reference it in custom tasks
        """
        value = (
            self.configuration.get("extension", {}).get(section, {}).get(setting, None)
        )
        if not value:
            raise ConfigError(
                f"Config file does not contain /extension/{section}/{setting}"
            )
        return value

    def __str__(self):
        return json.dumps(self._asdict())


class ConfigError(RuntimeError):
    """Error encountered during reading the config file.

    Arguments:
        msg (str): The message displayed to the user on error
    """

    def __init__(self, msg):
        """Set up."""
        super(ConfigError, self).__init__("%s" % (msg,))


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
    task_dict_filepath = os.path.abspath(configuration["storage"]["task_dict_filepath"])
    os.makedirs(os.path.dirname(database_filepath), exist_ok=True)
    if not os.path.exists(task_dict_filepath):
        raise ConfigError(f"No tasks file at configured path {task_dict_filepath}")

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

    commands = CommandList.from_yaml_obj(configuration.get("commands", {}))
    for cmdname, cmd in BUILTIN_COMMANDS.items():
        if cmdname in commands.commands:
            LOGGER.warning(
                f"A user-defined command '{cmdname}' conflicts with a built-in command of the same name. Overriding the user-defined command with the builtin."
            )
        commands.commands[cmdname] = cmd
    responses = ResponseList.from_yaml_obj(configuration.get("responses", []))

    appconfig = Configuration(
        configuration=configuration,
        config_filepath=filepath,
        database_filepath=database_filepath,
        store_filepath=store_filepath,
        task_dict_filepath=task_dict_filepath,
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

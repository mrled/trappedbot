#!/usr/bin/env python3

"""Implement utility functions for

- reading in the YAML config file
- performing the according initialization and set-up
"""

import json
import typing


class ConfigError(RuntimeError):
    """Error encountered during reading the config file.

    Arguments:
        msg (str): The message displayed to the user on error
    """

    def __init__(self, msg):
        """Set up."""
        super(ConfigError, self).__init__("%s" % (msg,))


class Configuration(typing.NamedTuple):
    """Application configuration"""

    configuration: typing.Dict = {}
    config_filepath: str = ""
    database_filepath: str = ""
    store_filepath: str = ""
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
    events: typing.Dict[str, "TrappedBotEventAction"] = {}
    commands: typing.Dict[str, "Command"] = {}
    responses: typing.List["Response"] = []

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

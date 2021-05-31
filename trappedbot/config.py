#!/usr/bin/env python3

"""Implement utility functions for

- reading in the YAML config file
- performing the according initialization and set-up
"""

import logging
import re
import os
import yaml
import sys
from typing import List, Any

import trappedbot


class ConfigError(RuntimeError):
    """Error encountered during reading the config file.

    Arguments:
        msg (str): The message displayed to the user on error
    """

    def __init__(self, msg):
        """Set up."""
        super(ConfigError, self).__init__("%s" % (msg,))


class Config(object):
    """Handle config file."""

    def __init__(self, filepath):
        """Initialize.

        Arguments:
            filepath (str): Path to config file
        """
        if not os.path.isfile(filepath):
            raise ConfigError(f"Config file '{filepath}' does not exist")

        # Load in the config file at the given filepath
        with open(filepath) as file_stream:
            self.config = yaml.safe_load(file_stream.read())

        # Logging setup
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s [%(levelname)s] %(message)s"
        )

        log_level = self._get_cfg(["logging", "level"], default="INFO")
        trappedbot.LOGGER.setLevel(log_level)

        file_logging_enabled = self._get_cfg(
            ["logging", "file_logging", "enabled"], default=False
        )
        file_logging_filepath = self._get_cfg(
            ["logging", "file_logging", "filepath"], default="bot.log"
        )
        if file_logging_enabled:
            handler = logging.FileHandler(file_logging_filepath)
            handler.setFormatter(formatter)
            trappedbot.LOGGER.addHandler(handler)

        console_logging_enabled = self._get_cfg(
            ["logging", "console_logging", "enabled"], default=True
        )
        if console_logging_enabled:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            trappedbot.LOGGER.addHandler(handler)

        # Storage setup
        self.database_filepath = self._get_cfg(
            os.path.abspath(["storage", "database_filepath"]), required=True
        )
        self.store_filepath = self._get_cfg(
            os.path.abspath(["storage", "store_filepath"]), required=True
        )
        self.command_dict_filepath = self._get_cfg(
            os.path.abspath(["storage", "command_dict_filepath"]), default=None
        )

        # Create the store folder
        os.makedirs(self.store_filepath, exist_ok=True)

        # Create the database parent folder
        os.makedirs(os.path.dirname(self.database_filepath), exist_ok=True)

        # Matrix bot account setup
        self.user_id = self._get_cfg(["matrix", "user_id"], required=True)
        if not re.match("@.*:.*", self.user_id):
            raise ConfigError("matrix.user_id must be in the form @name:domain")

        self.user_password = self._get_cfg(
            ["matrix", "user_password"], required=False, default=None
        )
        self.access_token = self._get_cfg(
            ["matrix", "access_token"], required=False, default=None
        )
        self.device_id = self._get_cfg(["matrix", "device_id"], required=True)
        self.device_name = self._get_cfg(
            ["matrix", "device_name"], default="nio-template"
        )
        self.homeserver_url = self._get_cfg(["matrix", "homeserver_url"], required=True)

        self.command_prefix = self._get_cfg(["command_prefix"], default="!c") + " "

        if not self.user_password and not self.access_token:
            raise ConfigError("Either user_password or access_token must be specified")

        self.trust_own_devices = self._get_cfg(
            ["matrix", "trust_own_devices"], default=False, required=False
        )
        self.change_device_name = self._get_cfg(
            ["matrix", "change_device_name"], default=False, required=False
        )

    def _get_cfg(
        self,
        path: List[str],
        default: Any = None,
        required: bool = True,
    ) -> Any:
        """Get a config option.

        Get a config option from a path and option name,
        specifying whether it is required.

        Raises
        ------
            ConfigError: If required is specified and the object is not found
                (and there is no default value provided),
                this error will be raised.

        """
        config = self.config
        for name in path:
            config = config.get(name)
            if config is None:
                if required:
                    raise ConfigError(f"Config option {'.'.join(path)} is required")
                return default
        return config

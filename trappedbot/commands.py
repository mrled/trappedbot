#!/usr/bin/env python3

"""Built-in commands

See the implemented sample bot commands of `echo`, `date`, `dir`, `help`,
and `whoami`? Have a close look at them and style your commands after these
example commands.
"""

import os
import re
import shlex
import subprocess
import traceback
import typing

from nio import AsyncClient
from nio.events.room_events import RoomMessageText
from nio.rooms import MatrixRoom

import trappedbot
from trappedbot import mxutil
from trappedbot.chat_functions import send_text_to_room
from trappedbot.config import Config
from trappedbot.taskdict import TaskDict, TaskMessageContext, TaskOutputFormat
from trappedbot.storage import Storage


class Command(object):
    """Use this class for your bot commands."""

    def __init__(
        self,
        client: AsyncClient,
        store: Storage,
        config: Config,
        taskdict: TaskDict,
        command: str,
        room: MatrixRoom,
        event: RoomMessageText,
    ):
        """Set up bot commands.

        Arguments:
        ---------
            client: The client to communicate with Matrix
            store: Bot storage
            config: Bot configuration parameters
            tasks: Tasks dictionary
            command: The command and arguments
            room: The room the command was sent in
            event: The event describing the command
        """
        self.client = client
        self.store = store
        self.config = config
        self.taskdict = taskdict
        self.command = command
        self.args = shlex.split(command)[1:]
        self.room = room
        self.event = event

    async def process(self):
        """Process the command."""

        trappedbot.LOGGER.debug(
            f"commands :: Command.process: {self.command} {self.room}"
        )

        if re.match(
            "^help$|^ayuda$|^man$|^manual$|^hilfe$|"
            "^je suis perdu$|^perdu$|^socorro$|^h$|"
            "^rescate$|^rescate .*|^help .*|^help.sh$",
            self.command.lower(),
        ):
            await self._show_help()
            return

        task = self.taskdict.find(self.command.lower())
        if not task:
            await self._unknown_command()
            return

        sender = mxutil.Mxid.fromstr(self.event.sender)
        if task.allow_untrusted:
            trappedbot.LOGGER.debug(
                f"Processing command {self.command} from sender {sender.mxid} because the invoked task {task.name} allows untrusted invocation"
            )
        elif sender.homeserver in task.allow_homeservers:
            trappedbot.LOGGER.debug(
                f"Processing command {self.command} from sender {sender.mxid} because the invoked task {task.name} allows users from homeserver {sender.homeserver}"
            )
        elif sender.mxid in task.allow_users:
            trappedbot.LOGGER.debug(
                f"Processing command {self.command} from sender {sender.mxid} because the invoked task {task.name} allows that user explicitly"
            )
        else:
            trappedbot.LOGGER.critical(
                f"Refusing to process command {self.command} from sender {sender.mxid} because the invoked task {task.name} does not permit execution by this user"
            )
            await send_text_to_room(
                self,
                client,
                self.room.room_id,
                "Not authorized: User {sender.mxid} is not authorized to run the task {task.name}",
                markdown_convert=False,
                code=False,
                split=None,
            )
            return

        taskctx = TaskMessageContext(self.event.sender, self.room.room_id)
        try:
            result = task.action(self.args, taskctx)
            markdown_convert = task.format == TaskOutputFormat.MARKDOWN
            code = task.format == TaskOutputFormat.CODE
            split = task.split
            trappedbot.LOGGER.debug(
                f"Task {task.name} completed successfully; replying with result:\n{result}"
            )
        except BaseException as exc:
            result = f"Error:\n{exc}\n{traceback.format_exc()}"
            markdown_convert = False
            # Always format errors in a code block
            code = True
            split = None
            trappedbot.LOGGER.debug(
                f"Task {task.name} encountered an error; replying with error:\n{result}"
            )

        await send_text_to_room(
            self.client,
            self.room.room_id,
            result,
            markdown_convert=markdown_convert,
            code=code,
            split=split,
        )

    async def _show_help(self):
        """Show the help text."""
        if not self.args:
            response = (
                "Hello, I am your bot! "
                "Use `help all` or `help commands` to view "
                "available commands."
            )
            await send_text_to_room(self.client, self.room.room_id, response)
            return

        topic = self.args[0]

        if topic == "rules":
            response = "These are the rules: Act responsibly."

        elif topic == "commands" or topic == "all":
            response = "Available commands:\n"
            for tname, task in self.taskdict.tasks.items():
                response += f"\n- {tname}: {task.help}"
            await send_text_to_room(
                self.client,
                self.room.room_id,
                response,
                markdown_convert=True,
                code=False,
                split=None,
            )
            return

        else:
            response = f"Unknown help topic `{topic}`!"

        await send_text_to_room(self.client, self.room.room_id, response)

    async def _unknown_command(self):
        await send_text_to_room(
            self.client,
            self.room.room_id,
            (
                f"Unknown command `{self.command}`. "
                "Try the `help` command for more information."
            ),
        )

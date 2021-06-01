#!/usr/bin/env python3

"""Built-in commands

See the implemented sample bot commands of `echo`, `date`, `dir`, `help`,
and `whoami`? Have a close look at them and style your commands after these
example commands.
"""

import re
import shlex
import traceback

from nio import AsyncClient
from nio.events.room_events import RoomMessageText
from nio.rooms import MatrixRoom

import trappedbot
from trappedbot import mxutil
from trappedbot.chat_functions import send_text_to_room
from trappedbot.taskdict import TaskDict, TaskMessageContext
from trappedbot.storage import Storage


class Command(object):
    """Use this class for your bot commands."""

    def __init__(
        self,
        client: AsyncClient,
        store: Storage,
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
            tasks: Tasks dictionary
            command: The command and arguments
            room: The room the command was sent in
            event: The event describing the command
        """
        self.client = client
        self.store = store
        self.taskdict = taskdict

        # Split the command into arguments, and always user lower case for the command name
        # (No reason to allow commands like 'host' and 'Host' to be different, right?)
        cmdsplit = shlex.split(command)
        cmdsplit[0] = cmdsplit[0].lower()

        self.rawcmd = command
        self.cmdsplit = cmdsplit
        self.room = room
        self.event = event

    async def process(self):
        """Process the command."""

        trappedbot.LOGGER.debug(
            f"commands :: Command.process: {self.rawcmd} {self.room}"
        )

        if re.match(
            "^help$|^ayuda$|^man$|^manual$|^hilfe$|"
            "^je suis perdu$|^perdu$|^socorro$|^h$|"
            "^rescate$|^rescate .*|^help .*|^help.sh$",
            self.cmdsplit[0],
        ):
            await self._show_help()
            return

        task = self.taskdict.find(self.cmdsplit[0])
        if not task:
            await self._unknown_command()
            return

        sender = mxutil.Mxid.fromstr(self.event.sender)
        if sender.mxid in trappedbot.APPCONFIG.trusted_users:
            trappedbot.LOGGER.debug(
                f"Processing command {self.rawcmd} from sender {sender.mxid} because sender is in the list of trusted users"
            )
        elif task.allow_untrusted:
            trappedbot.LOGGER.debug(
                f"Processing command {self.rawcmd} from sender {sender.mxid} because the invoked task {task.name} allows untrusted invocation"
            )
        elif sender.homeserver in task.allow_homeservers:
            trappedbot.LOGGER.debug(
                f"Processing command {self.rawcmd} from sender {sender.mxid} because the invoked task {task.name} allows users from homeserver {sender.homeserver}"
            )
        elif sender.mxid in task.allow_users:
            trappedbot.LOGGER.debug(
                f"Processing command {self.rawcmd} from sender {sender.mxid} because the invoked task {task.name} allows that user explicitly"
            )
        else:
            trappedbot.LOGGER.critical(
                f"Refusing to process command {self.rawcmd} from sender {sender.mxid} because the invoked task {task.name} does not permit execution by this user"
            )
            await send_text_to_room(
                self.client,
                self.room.room_id,
                f"Not authorized: User {sender.mxid} is not authorized to run the task {task.name}",
                format=mxutil.MessageFormat.NATURAL,
                split=None,
            )
            return

        taskctx = TaskMessageContext(self.event.sender, self.room.room_id)
        try:
            result = task.action(self.cmdsplit[1:], taskctx)
            format = task.format
            split = task.split
            trappedbot.LOGGER.debug(
                f"Task {task.name} completed successfully; replying with result:\n{result}"
            )
        except BaseException as exc:
            result = f"Error:\n{exc}\n{traceback.format_exc()}"
            # Always format errors in a code block
            format = mxutil.MessageFormat.CODE
            split = None
            trappedbot.LOGGER.debug(
                f"Task {task.name} encountered an error; replying with error:\n{result}"
            )

        await send_text_to_room(
            self.client,
            self.room.room_id,
            result,
            format=format,
            split=split,
        )

    async def _show_help(self):
        """Show the help text."""
        if len(self.cmdsplit) == 1:
            response = (
                "Hello, I am your bot! "
                "Use `help all` or `help commands` to view "
                "available commands."
            )
            await send_text_to_room(self.client, self.room.room_id, response)
            return

        topic = self.cmdsplit[1]

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
                format=mxutil.MessageFormat.MARKDOWN,
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
            f"Unknown command `{self.rawcmd}`. Try the `help` command for more information.",
            format=mxutil.MessageFormat.MARKDOWN,
        )

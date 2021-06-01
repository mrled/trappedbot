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
from trappedbot.taskdict import TaskDict, TaskOutputFormat
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
            # TODO: Have the bot reply when this happens
            return

        await self._os_cmd(
            cmd=task.systemcmd,
            args=self.args,
            markdown_convert=task.format == TaskOutputFormat.MARKDOWN,
            code=task.format == TaskOutputFormat.CODE,
            split=task.split,
        )
        return

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

    async def _os_cmd(
        self,
        cmd: str,
        args: list,
        markdown_convert=True,
        code=False,
        split=None,
    ):
        """Pass generic command on to the operating system.

        cmd (str): string of the command including any path,
            make sure command is found
            by operating system in its PATH for executables
            e.g. "date" for OS date command.
            cmd does not include any arguments.
            Valid example of cmd: "date"
            Invalid example for cmd: "echo 'Date'; date --utc"
            Invalid example for cmd: "echo 'Date' && date --utc"
            Invalid example for cmd: "TZ='America/Los_Angeles' date"
            If you have commands that consist of more than 1 command,
            put them into a shell or .bat script and call that script
            with any necessary arguments.
        args (list): list of arguments
            Valid example: [ '--verbose', '--abc', '-d="hello world"']
        markdown_convert (bool): value for how to format response
        code (bool): value for how to format response
        """
        try:
            # create a combined argv list, e.g. ['date', '--utc']
            argv_list = [cmd] + args
            trappedbot.LOGGER.debug(
                f'OS command "{argv_list[0]}" with ' f'args: "{argv_list[1:]}"'
            )

            # Set environment variables for the subprocess here.
            # Env variables like PATH, etc. are already set. In order to not lose
            # any set env variables we must merge existing env variables with the
            # new env variable(s). subprocess.Popen must be called with the
            # complete combined list.
            new_env = os.environ.copy()
            new_env["ENO_SENDER"] = self.event.sender

            run = subprocess.Popen(
                argv_list,  # list of argv
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=new_env,
            )
            output, std_err = run.communicate()
            output = output.strip()
            std_err = std_err.strip()
            if run.returncode != 0:
                trappedbot.LOGGER.debug(
                    f"Bot command {cmd} exited with return "
                    f"code {run.returncode} and "
                    f'stderr as "{std_err}" and '
                    f'stdout as "{output}"'
                )
                output = (
                    f"*** Error: command {cmd} returned error "
                    f"code {run.returncode}. ***\n{std_err}\n{output}"
                )
            response = output
        except Exception:
            response = (
                "Bot encountered an error. Here is the stack trace: \n"
                + traceback.format_exc()
            )
            code = True  # format stack traces as code
        trappedbot.LOGGER.debug(f"Sending this reply back: {response}")
        await send_text_to_room(
            self.client,
            self.room.room_id,
            response,
            markdown_convert=markdown_convert,
            code=code,
            split=split,
        )

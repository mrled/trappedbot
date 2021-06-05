"""Built-in commands

See the implemented sample bot commands of `echo`, `date`, `dir`, `help`,
and `whoami`? Have a close look at them and style your commands after these
example commands.
"""

import shlex
import traceback
from typing import List, Optional

from nio import AsyncClient
from nio.events.room_events import RoomMessageText
from nio.rooms import MatrixRoom

from trappedbot import appconfig
from trappedbot.applogger import LOGGER
from trappedbot.mxutil import MessageFormat, Mxid
from trappedbot.chat_functions import send_text_to_room
from trappedbot.tasks.task import Task, TaskMessageContext


class Command(object):
    """A command that a bot can perform

    name: The word that activates this command
    task: The task to perform
    help: Help text for the command
    allow_untrusted: Allow any user to run this command?
    allow_homeservers: Allow any user from these homeservers to run this command?
    allow_users: Allow any user in this list to run this command?
    """

    def __init__(
        self,
        name: str,
        task: Task,
        # This isn't a NamedTuple because I want to be able to pass help=None
        # and have it use fallback text. Sigh.
        help: Optional[str] = None,
        allow_untrusted: bool = False,
        allow_homeservers: Optional[List[str]] = None,
        allow_users: Optional[List[str]] = None,
    ):
        self.name = name
        self.task = task
        self.help = help or "No help available for this command"
        self.allow_untrusted = allow_untrusted
        self.allow_homeservers = allow_homeservers or []
        self.allow_users = allow_users or []


async def process_command(
    client: AsyncClient,
    input: str,
    room: MatrixRoom,
    event: RoomMessageText,
) -> None:
    """Process the command."""

    config = appconfig.get()

    # Split the command into arguments, and always user lower case for the command name
    # (No reason to allow commands like 'host' and 'Host' to be different, right?)
    cmdsplit = shlex.split(input)
    cmdsplit[0] = cmdsplit[0].lower()
    cmdname = cmdsplit[0]

    LOGGER.debug(f"commands :: Command.process: {input} {room}")

    command = config.commands.get(cmdname)
    if not command:
        await send_text_to_room(
            client,
            room.room_id,
            f"Unknown command `{input}`. Try the `help` command for more information.",
            format=MessageFormat.MARKDOWN,
        )
        return

    sender = Mxid.fromstr(event.sender)
    if sender.mxid in config.trusted_users:
        LOGGER.debug(
            f"Processing command {input} from sender {sender.mxid} because sender is in the list of trusted users"
        )
    elif command.allow_untrusted:
        LOGGER.debug(
            f"Processing command {input} from sender {sender.mxid} because the invoked command {command.name} allows untrusted invocation"
        )
    elif command.allow_homeservers and sender.homeserver in command.allow_homeservers:
        LOGGER.debug(
            f"Processing command {input} from sender {sender.mxid} because the invoked command {command.name} allows users from homeserver {sender.homeserver}"
        )
    elif command.allow_users and sender.mxid in command.allow_users:
        LOGGER.debug(
            f"Processing command {input} from sender {sender.mxid} because the invoked command {command.name} allows that user explicitly"
        )
    else:
        LOGGER.critical(
            f"Refusing to process command {input} from sender {sender.mxid} because the invoked command {command.name} does not permit execution by this user"
        )
        await send_text_to_room(
            client,
            room.room_id,
            f"Not authorized: User {sender.mxid} is not authorized to run the command {command.name}",
            format=MessageFormat.NATURAL,
            split=None,
        )
        return

    taskctx = TaskMessageContext(event.sender, room.room_id)
    try:
        result = command.task.taskfunc(cmdsplit[1:], taskctx)
        message = result.output
        format = result.format
        split = result.split
        LOGGER.debug(
            f"Task {command.task.name} completed successfully; replying with output:\n{message}"
        )
    except BaseException as exc:
        message = f"Error:\n{exc}\n{traceback.format_exc()}"
        # Always format errors in a code block
        format = MessageFormat.CODE
        split = None
        LOGGER.debug(
            f"Task {command.task.name} encountered an error; replying with error:\n{message}"
        )

    await send_text_to_room(
        client,
        room.room_id,
        message,
        format=format,
        split=split,
    )
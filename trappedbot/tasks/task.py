import os
import re
import subprocess
import typing

import trappedbot
from trappedbot.mxutil import MessageFormat


class TaskMessageContext(typing.NamedTuple):
    """A container for message context that can be passed to a TaskFunction"""

    sender: str
    room: str


class TaskResult(typing.NamedTuple):
    """The result of a TaskFunction"""

    output: str
    format: MessageFormat
    split: typing.Optional[str] = None


# A function that we can use to run code for our task
# TaskFunction callables take a list of arguments, and a set of message context
# The list of arguments comes from the chat command;
# e.g. if you send the bot a command like 'echo 1 2 3' the list of arguments
# is ['1', '2', '3'].
# The message context contains the sender, room, and possibly other metadata,
# and can be used to write tasks that take these values into account,
# for instance replying to users by name.
TaskFunction = typing.Callable[[typing.List[str], TaskMessageContext], TaskResult]


def command2taskfunc(cmd: str) -> TaskFunction:
    """Return a TaskFunction that runs an external program"""

    def _run_systemcmd(
        arguments: typing.List[str], context: TaskMessageContext
    ) -> TaskResult:
        """Run an external program"""

        fullcmd = [cmd] + arguments
        trappedbot.LOGGER.debug(f"Running system command {fullcmd}")

        env = os.environ.copy()
        env["MATRIX_SENDER"] = context.sender
        env["MATRIX_ROOM"] = context.room

        proc = subprocess.Popen(
            fullcmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        stdout, stderr = proc.communicate()
        stdout = stdout.strip()
        stderr = stderr.strip()

        if proc.returncode != 0:
            raise subprocess.CalledProcessError(
                proc.returncode, fullcmd, stdout, stderr
            )

        return TaskResult(stdout, MessageFormat.CODE)

    return _run_systemcmd


def constant2taskfunc(
    value: str, format: MessageFormat = MessageFormat.NATURAL
) -> TaskFunction:
    """Given a constant, return a TaskFunction"""

    def _result_func(
        arguments: typing.List[str], context: TaskMessageContext
    ) -> TaskResult:
        return TaskResult(value, format)

    return _result_func


class Task(typing.NamedTuple):
    """A task that our bot can perform
    Arguments:
        name:                   The name of the task.
        regex:                  Regex for whether the task matches.
                                This allows us to set task aliases.
        taskfunc:               A TaskFunction callable.
        help:                   Help text for the user.
        format:                 The format of the response.
        split:                  If set, split response into multiple messages
                                whenever this string occurs in the taskfunc output.
        allow_untrusted:        Allow ALL users ANYWHERE to run this task. BE CAREFUL!
                                If true, will allow any user regardless of other allow_* settings.
        allow_homeservers:      Allow ALL users of ANY homeserver in this list to run this task.
        allow_users:            Allow ONLY mxids listed here.
    """

    name: str
    taskfunc: TaskFunction
    regex: typing.Optional[str] = None
    help: typing.Optional[str] = "No help defined for this command"
    format: typing.Optional[MessageFormat] = MessageFormat.NATURAL
    split: typing.Optional[str] = None
    allow_untrusted: typing.Optional[bool] = False
    allow_homeservers: typing.Optional[typing.List[str]] = None
    allow_users: typing.Optional[typing.List[str]] = None

    def aliasmatch(self, alias):
        """Return whether the task's regex matches the provided alias"""
        if not self.regex:
            return False
        return re.match(self.regex, alias)
"""Built-in commands for the bot

These are not restricted to external system commands, but can just return Python code
"""

import platform
import sys
import typing

import trappedbot
from trappedbot.mxutil import MessageFormat
from trappedbot.tasks.task import Task, TaskMessageContext
from trappedbot.tasks.taskutil import constant2taskfunc


def echo(arguments: typing.List[str], _context: TaskMessageContext) -> str:
    return " ".join(arguments)


def dbgecho(arguments: typing.List[str], context: TaskMessageContext) -> str:
    return f"{context.sender} in room {context.room} said {' '.join(arguments)}"


def platinfo(_arguments: typing.List[str], _context: TaskMessageContext) -> str:
    info = {
        "Python version": " ".join(sys.version.split("\n")),
        "Operating system": platform.system(),
        "Kernel version": platform.version(),
        "Python platform": platform.platform(),
        "Machine architecture": platform.machine(),
    }
    result = "<table>"
    for k, v in info.items():
        result += f"<tr><th>{k}</th><td>{v}</td></tr>"
    result += "</table>"
    return result


# When the bot is started without a task definition file, the help/format/etc
# of these tasks is used, but when the bot is started with a task definition
# file that references these builtins, the help/format/etc from the task
# definition file are used, and these here are ignored.
BUILTIN_TASKS = {
    "version": Task(
        "version",
        taskfunc=constant2taskfunc(trappedbot.version_cute()),
        help="Bot version",
        format=MessageFormat.CODE,
        allow_untrusted=True,
    ),
    "echo": Task(
        "echo",
        taskfunc=echo,
        help="Echo back",
        allow_untrusted=True,
    ),
    "dbgecho": Task(
        "dbgecho",
        taskfunc=dbgecho,
        help="Echo back, with debugging info",
        allow_untrusted=True,
        format=MessageFormat.MARKDOWN,
    ),
    "platinfo": Task(
        "platinfo",
        taskfunc=platinfo,
        help="Show platform info for host running bot",
        allow_untrusted=True,
        format=MessageFormat.FORMATTED,
    ),
}

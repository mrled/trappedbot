"""Built-in commands for the bot

These are not restricted to external system commands, but can just return Python code
"""

import platform
import sys
import textwrap
import typing

import trappedbot
from trappedbot.taskdict import Task, TaskFunction, TaskMessageContext
from trappedbot.mxutil import MessageFormat


def constant2taskfunc(value: str) -> TaskFunction:
    """Given a constant, return a TaskFunction"""

    def _result_func(arguments: typing.List[str], context: TaskMessageContext) -> str:
        return value

    return _result_func


def echo(arguments: typing.List[str], context: TaskMessageContext) -> str:
    return " ".join(arguments)


def dbgecho(arguments: typing.List[str], context: TaskMessageContext) -> str:
    return f"{context.sender} in room {context.room} said {' '.join(arguments)}"


def platinfo(arguments: typing.List[str], context: TaskMessageContext) -> str:
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


BUILTIN_TASKS = [
    Task(
        "version",
        taskfunc=constant2taskfunc(trappedbot.version_cute()),
        help="Bot version",
        format=MessageFormat.CODE,
        allow_untrusted=True,
    ),
    Task(
        "echo",
        taskfunc=echo,
        help="Echo back",
        allow_untrusted=True,
    ),
    Task(
        "dbgecho",
        taskfunc=dbgecho,
        help="Echo back, with debugging info",
        allow_untrusted=True,
        format=MessageFormat.MARKDOWN,
    ),
    Task(
        "platinfo",
        taskfunc=platinfo,
        help="Show platform info for host running bot",
        allow_untrusted=True,
        format=MessageFormat.FORMATTED,
    ),
]

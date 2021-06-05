"""Built-in commands for the bot

These are not restricted to external system commands, but can just return Python code
"""

import platform
import sys
import typing

from trappedbot import appconfig
from trappedbot.constants import HELP_TRAPPED_MSG
from trappedbot.mxutil import MessageFormat
from trappedbot.tasks.task import (
    Task,
    TaskMessageContext,
    TaskResult,
    constant2taskfunc,
)
from trappedbot.version import version_cute


def builtin_task_echo(
    arguments: typing.List[str], _context: TaskMessageContext
) -> TaskResult:
    return TaskResult(" ".join(arguments), MessageFormat.NATURAL)


def builtin_task_dbgecho(
    arguments: typing.List[str], context: TaskMessageContext
) -> TaskResult:
    return TaskResult(
        f"{context.sender} in room {context.room} said {' '.join(arguments)}",
        MessageFormat.NATURAL,
    )


def builtin_task_platinfo(
    _arguments: typing.List[str], _context: TaskMessageContext
) -> TaskResult:
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
    return TaskResult(result, MessageFormat.FORMATTED)


def builtin_task_help(
    arguments: typing.List[str], context: TaskMessageContext
) -> TaskResult:
    config = appconfig.get()
    format = MessageFormat.NATURAL
    if len(arguments) == 0:
        output = (
            f"{HELP_TRAPPED_MSG} Use 'help commands' to view things I can do from here"
        )
    elif len(arguments) == 1:
        topic = arguments[0]
        if topic == "commands":
            outlines = []
            for cname, cmd in config.commands.commands.items():
                outlines.append(f"- {cname}: {cmd.help}")
            output = "\n".join(outlines)
            format = MessageFormat.MARKDOWN
        elif (command := config.commands.commands.get(topic)) :
            output = f"{topic}: {command.help}"
        else:
            output = f"Unknown help topic '{topic}'"
    else:
        output = f"Not sure how to help you with '{arguments}'"
    return TaskResult(output, format)


# TODO: do I need to keep track of the name in both the dict and the task itself?

# When the bot is started without a task definition file, the help/format/etc
# of these tasks is used, but when the bot is started with a task definition
# file that references these builtins, the help/format/etc from the task
# definition file are used, and these here are ignored.
BUILTIN_TASKS = {
    "version": Task(
        "version",
        taskfunc=constant2taskfunc(version_cute(), format=MessageFormat.CODE),
    ),
    "help": Task("help", taskfunc=builtin_task_help),
    "echo": Task(
        "echo",
        taskfunc=builtin_task_echo,
    ),
    "dbgecho": Task(
        "dbgecho",
        taskfunc=builtin_task_dbgecho,
    ),
    "platinfo": Task(
        "platinfo",
        taskfunc=builtin_task_platinfo,
    ),
}

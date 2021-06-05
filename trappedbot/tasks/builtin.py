"""Built-in commands for the bot

These are not restricted to external system commands, but can just return Python code
"""

import dataclasses
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


@dataclasses.dataclass
class HelpTopic:
    name: str
    help: str
    detail: str


def builtin_task_help(
    arguments: typing.List[str], context: TaskMessageContext
) -> TaskResult:
    config = appconfig.get()
    format = MessageFormat.MARKDOWN

    topic_commands_lines = []
    for cname, cmd in config.commands.commands.items():
        topic_commands_lines.append(f"- `{config.command_prefix} {cname}`: {cmd.help}")

    topic_responses_lines = []
    for reply in config.responses.responses:
        topic_responses_lines.append(f"- `{reply.regex.pattern}` => `{reply.message}`")

    help_topics = HelpTopic("topics", "This help", "PLACEHOLDER")

    topics = [
        help_topics,
        HelpTopic(
            "commands", "Show a list of commands", "\n".join(topic_commands_lines)
        ),
        HelpTopic(
            "responses", "Show a list of responses", "\n".join(topic_responses_lines)
        ),
    ]
    topicdict = {t.name: t for t in topics}

    help_topics_lines = []
    for t in topics:
        help_topics_lines.append(f"- **{t.name}**: {t.help}")
    help_topics.detail = "\n".join(help_topics_lines)

    if len(arguments) == 0:
        outlines = [f"{HELP_TRAPPED_MSG}", ""]
        for t in topics:
            outlines += [f"- `{config.command_prefix} help {t.name}`: {t.help}"]
        output = "\n".join(outlines)
    else:
        topic = arguments[0]
        if topic in topicdict:
            output = topicdict[topic].detail
        else:
            output = f"Unknown help command '{arguments}'"
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

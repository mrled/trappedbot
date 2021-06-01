"""Built-in commands for the bot

These are not restricted to external system commands, but can just return Python code
"""

import typing

import trappedbot
from trappedbot.taskdict import Task, TaskFunction, TaskMessageContext, TaskOutputFormat


def constant2taskfunc(value: str) -> TaskFunction:
    """Given a constant, return a TaskFunction"""

    def _result_func(arguments: typing.List[str], context=TaskMessageContext) -> str:
        return value

    return _result_func


BUILTIN_TASKS = [
    Task(
        "version",
        constant2taskfunc(trappedbot.version_cute()),
        help="Bot version",
        format=TaskOutputFormat.CODE,
        allow_untrusted=True,
    ),
]

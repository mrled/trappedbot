"""Task-related utilities"""

import typing

from trappedbot.tasks.task import TaskFunction, TaskMessageContext


def constant2taskfunc(value: str) -> TaskFunction:
    """Given a constant, return a TaskFunction"""

    def _result_func(arguments: typing.List[str], context: TaskMessageContext) -> str:
        return value

    return _result_func

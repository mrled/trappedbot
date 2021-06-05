"""Example external task

To define an external task, you just have to create a Python script with a
function called 'trappedbot_task' which takes two arguments:

1.  A list of string parameters to the task.
    This are what the user typed after the bot command (if anything).
    E.g. if your command is 'echo', the user might send the bot a message like
    'echo one two three'; this parameter will be a list of
    ['one', 'two', 'three'].
2.  A context object containing information from the chat message.
    See taskdict.TaskMessageContext.
    Currently, this contains these properties:
    sender:     The mxid of the sender, like '@user:example.com'
    room:       The room ID, like !ickuLvUxvGXCJsZcpV:example.com

The function then must return a TaskResult containing the output to the channel
and formatting information.

One final note: an external Python task can be a Python package (a directory
with an __init__.py file) instead of simple Python modules (a script ending in
.py).
"""

import typing

from trappedbot.extensions import (
    MessageFormat,
    TaskMessageContext,
    TaskResult,
)


def trappedbot_task(
    arguments: typing.List[str], context: TaskMessageContext
) -> TaskResult:
    """A simple echo command"""
    return TaskResult(
        f"User {context.sender} in room {context.room} says '{' '.join(arguments)}'",
        MessageFormat.NATURAL,
    )

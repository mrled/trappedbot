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

The function should return a string that can be

See the example in tasks.example.yml for how to reference this.

TODO:   Have all Python tasks return their format type too.
        This means the implementation can change and configured tasks do not
        need to be updated.
You can return Markdown or Matrix custom HTML (which is a simplified subset of
HTML but includes nice formatting options like tables). If you do, the format
must be specified in your tasks yml file.

One final note: an external Python task can be a Python package (a directory
with an __init__.py file) instead of simple Python modules (a script ending in
.py).
"""

import typing

from trappedbot.tasks.task import TaskMessageContext


def trappedbot_task(arguments: typing.List[str], context: TaskMessageContext) -> str:
    """A simple echo command"""
    return f"User {context.sender} in room {context.room} says '{' '.join(arguments)}'"

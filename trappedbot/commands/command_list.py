"""Task dictionary
"""

import typing

import trappedbot
from trappedbot.applogger import LOGGER
from trappedbot.commands.command import Command
from trappedbot.tasks.builtin import BUILTIN_TASKS
from trappedbot.tasks.dynload import trappedbot_dynload_for_taskfunc
from trappedbot.tasks.task import Task, systemcmd2taskfunc


def yamlobj2command(
    name: str,
    yamlobj: typing.Dict,
) -> typing.Optional[Command]:
    if yamlobj.get("builtin"):
        taskfunc = BUILTIN_TASKS[name].taskfunc
    elif (cmd := yamlobj.get("systemcmd")) :
        taskfunc = systemcmd2taskfunc(cmd)
    elif (modpath := yamlobj.get("modulepath")) :
        taskfunc_opt = trappedbot_dynload_for_taskfunc(name, modpath)
        if not taskfunc_opt:
            LOGGER.critical(f"Unable to load task {name}")
            return None
        else:
            # TODO: bleh is this the best pattern
            taskfunc = taskfunc_opt
    else:
        LOGGER.critical(f"Unknown task type for task {name}")
        return None
    return Command(
        name,
        Task(
            name,
            taskfunc,
            split=yamlobj.get("split"),
        ),
    )


class CommandList:
    """A list of commands that our bot can perform"""

    def __init__(self, commands: typing.Dict[str, Command]):
        self.commands = commands

    @classmethod
    def from_yaml_obj(cls, commands_yaml_obj: typing.Any):
        """Return a CommandList from a YAML object"""
        commands: typing.Dict[str, Command] = {}
        for cname, cdefn in commands_yaml_obj.items():
            if (command := yamlobj2command(cname, cdefn)) :
                commands[cname] = command
        return cls(commands)

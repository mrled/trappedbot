"""Task dictionary
"""

import typing

from trappedbot.applogger import LOGGER
from trappedbot.commands.command import Command
from trappedbot.tasks.builtin import BUILTIN_TASKS
from trappedbot.tasks.dynload import trappedbot_dynload_for_taskfunc
from trappedbot.tasks.task import Task, systemcmd2taskfunc


def yamlobj2command(
    name: str,
    yamlobj: typing.Dict,
) -> typing.Optional[Command]:
    if (builtin_name := yamlobj.get("builtin")) :
        taskfunc = BUILTIN_TASKS[builtin_name].taskfunc
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
        help=yamlobj.get("help", None),
        allow_untrusted=yamlobj.get("allow_untrusted", False),
        allow_homeservers=yamlobj.get("allow_homeservers", []),
        allow_users=yamlobj.get("allow_users", []),
    )


def yamlobj2cmddict(commands_yaml_obj: typing.Any) -> typing.Dict[str, Command]:
    """Return a CommandList from a YAML object"""
    commands: typing.Dict[str, Command] = {}
    for cname, cdefn in commands_yaml_obj.items():
        if (command := yamlobj2command(cname, cdefn)) :
            commands[cname] = command
    return commands

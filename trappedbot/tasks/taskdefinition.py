"""Task dictionary
"""

import os
import re
import typing

import yaml

import trappedbot
from trappedbot.mxutil import MessageFormat
from trappedbot.tasks.builtin import BUILTIN_TASKS
from trappedbot.tasks.dynload import trappedbot_dynload_for_taskfunc
from trappedbot.tasks.responses import Response
from trappedbot.tasks.task import Task, command2taskfunc


class TaskDefinitionException(BaseException):
    def __init__(self, taskname: str, msg: str):
        self.taskname = taskname
        self.msg = msg

    def __str__(self):
        return f"Error defining task {self.taskname}: {self.msg}"


def yamlobj2task(
    name: str,
    yamlobj: typing.Dict,
) -> typing.Optional[Task]:
    if yamlobj.get("builtin"):
        taskfunc = BUILTIN_TASKS[name].taskfunc
    elif (cmd := yamlobj.get("systemcmd")) :
        taskfunc = command2taskfunc(cmd)
    elif (modpath := yamlobj.get("modulepath")) :
        taskfunc_opt = trappedbot_dynload_for_taskfunc(name, modpath)
        if not taskfunc_opt:
            trappedbot.LOGGER.critical(f"Unable to load task {name}")
            return None
        else:
            # TODO: bleh is this the best pattern
            taskfunc = taskfunc_opt
    else:
        trappedbot.LOGGER.critical(f"Unknown task type for task {name}")
        return None
    return Task(
        name,
        taskfunc,
        regex=yamlobj.get("regex"),
        help=yamlobj.get("help"),
        split=yamlobj.get("split"),
        allow_untrusted=yamlobj.get("allow_untrusted"),
        allow_homeservers=yamlobj.get("allow_homeservers"),
        allow_users=yamlobj.get("allow_users"),
    )


def yamlobj2response(idx: int, yamlobj: typing.Dict) -> typing.Optional[Response]:
    """Make a new Response object from a YAML object"""
    flags = re.IGNORECASE if yamlobj.get("ignorecase", False) else None
    try:
        regex_str = yamlobj["regex"]
        try:
            if flags is not None:
                regex = re.compile(regex_str, flags=flags)
            else:
                regex = re.compile(regex_str)
        except BaseException as exc:
            trappedbot.LOGGER.critical(
                f"Failed to compile regex {regex_str} for response definition found at index {idx} with exception {exc}, ignoring..."
            )
            return None
        return Response(regex, yamlobj["response"])
    except BaseException:
        trappedbot.LOGGER.critical(
            f"Invalid response definition found at index {idx}, ignoring..."
        )
        return None


class TaskDefinition:
    """The task dictionary.

    Contains all the tasks that our bot can perform.
    """

    def __init__(self, tasks_dict_filepath):
        """Initialize task dictionary."""
        self.tasks: typing.Dict[str, Task] = {}
        self.responses: typing.List[Response] = []
        self.load(tasks_dict_filepath)

    def load(self, tasks_dict_filepath):
        """Try loading the task dictionary.

        Arguments:
        ----------
            tasks_dict_filepath (string): path to task dictionary.
        """
        try:
            with open(tasks_dict_filepath) as fobj:
                trappedbot.LOGGER.debug(
                    f"Loading task dictionary at {tasks_dict_filepath}"
                )
                loaded_tasks = yaml.safe_load(fobj.read())

            if "tasks" in loaded_tasks:
                for tname, tdefn in loaded_tasks["tasks"].items():
                    if (task := yamlobj2task(tname, tdefn)) :
                        self.tasks[tname] = task

            if "responses" in loaded_tasks:
                for idx, rdefn in enumerate(loaded_tasks["responses"]):
                    if (response := yamlobj2response(idx, rdefn)) :
                        self.responses.append(response)

            if "paths" in loaded_tasks:
                os.environ["PATH"] = os.pathsep.join(
                    loaded_tasks["paths"] + [os.environ["PATH"]]
                )
                trappedbot.LOGGER.debug(f'Path modified. Now: {os.environ["PATH"]}.')

        except FileNotFoundError:
            trappedbot.LOGGER.error(f"File not found: {tasks_dict_filepath}")

        return

    def find(self, string: str) -> typing.Union[Task, None]:
        """If the input matches one of the tasks' names, return it."""
        if string in self.tasks.keys():
            return self.tasks[string]
        else:
            for task in self.tasks.values():
                if task.aliasmatch(string):
                    return task
        return None

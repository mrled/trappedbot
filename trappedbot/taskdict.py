"""Task dictionary
"""

import enum
import os
import re
import subprocess
import typing

import yaml

import trappedbot


class TaskDefinitionException(BaseException):
    def __init__(self, taskname: str, msg: str):
        self.taskname = taskname
        self.msg = msg

    def __str__(self):
        return f"Error defining task {self.taskname}: {self.msg}"


class TaskOutputFormat(enum.Enum):
    """Format for sending command output

    NATURAL:    Default
    MARKDOWN:   Command output is markdown, so convert to HTML before sending to Matrix
    CODE:       Send command output in fixed-width <pre><code> block
    """

    NATURAL = enum.auto()
    MARKDOWN = enum.auto()
    CODE = enum.auto()


class TaskMessageContext(typing.NamedTuple):
    """A container for message context that can be passed to a TaskFunction"""

    sender: str
    room: str


# A function that we can use to run code for our task
# TaskFunction callables take a list of arguments, and a set of message context
TaskFunction = typing.Callable[[typing.List[str], TaskMessageContext], str]


def command2taskfunc(cmd: str) -> TaskFunction:
    """Return a TaskFunction that runs an external program"""

    def _run_systemcmd(arguments: typing.List[str], context: TaskMessageContext) -> str:
        """Run an external program"""

        fullcmd = [cmd] + arguments
        trappedbot.LOGGER.debug(f"Running system command {fullcmd}")

        env = os.environ.copy()
        env["MATRIX_SENDER"] = context.sender

        proc = subprocess.Popen(
            fullcmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        stdout, stderr = proc.communicate()
        stdout = stdout.strip()
        stderr = stderr.strip()

        if proc.returncode != 0:
            raise subprocess.CalledProcessError(
                proc.returncode, fullcmd, stdout, stderr
            )

        return stdout

    return _run_systemcmd


class Task(object):
    """A task that our bot can perform
    Arguments:
        name:                   The name of the task.
        regex:                  Regex for whether the task matches.
                                This allows us to set task aliases.
        taskfunc:               A TaskFunction callable.
                                May not be specified with systemcmd.
        systemcmd:              A system command to run.
                                Must be in the bot's path.
                                Arguments to the command are passed on the commandline.
                                May not be specified with taskfunc.
        help:                   Help text for the user
        format:                 A value from TaskOutputFormat enum
        split:                  If set, split with this value
        allow_untrusted:        Allow ALL users ANYWHERE to run this task. BE CAREFUL!
                                If true, will allow any user regardless of other allow_* settings.
        allow_homeservers:      Allow ALL users of ANY homeserver in this list to run this task.
        allow_users:            Allow ONLY mxids listed here.
    """

    def __init__(
        self,
        name: str,
        taskfunc: typing.Optional[TaskFunction] = None,
        systemcmd: typing.Optional[str] = None,
        regex: typing.Optional[str] = None,
        help: str = "No help defined for this command",
        format: TaskOutputFormat = TaskOutputFormat.NATURAL,
        split: typing.Optional[str] = None,
        allow_untrusted: bool = False,
        allow_homeservers: typing.Optional[typing.List[str]] = None,
        allow_users: typing.Optional[typing.List[str]] = None,
    ):

        if (taskfunc and systemcmd) or (not taskfunc and not systemcmd):
            raise TaskDefinitionException(
                name, "Define exactly one of taskfunc, systemcmd"
            )
        elif taskfunc:
            self.action = taskfunc
        elif systemcmd:
            self.action = command2taskfunc(systemcmd)
        else:
            raise TaskDefinitionException(name, "Unexpected task definition error")

        self.name = name
        self.regex = regex
        self.help = help
        self.format = format
        self.split = split
        self.allow_untrusted = allow_untrusted or False
        self.allow_homeservers = allow_homeservers or []
        self.allow_users = allow_users or []

    def aliasmatch(self, alias):
        """Return whether the task's regex matches the provided alias"""
        if not self.regex:
            return False
        return re.match(self.regex, alias)


# TODO: Make TaskDict a true dict subclass
class TaskDict:
    """The task dictionary.

    Contains all the tasks that our bot can perform.
    """

    def __init__(self, tasks_dict_filepath):
        """Initialize task dictionary."""
        self.tasks: typing.Dict[str, Task] = {}
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
                    self.tasks[tname] = Task(name=tname, **tdefn)

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

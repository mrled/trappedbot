"""The trappedbot extensions namespace

Things in this namespace are guaranteed not to change between major version.

* appconfig:
  The application configuration.
  The whole config is exposed because the configuration must be stable as well anyway.
* LOGGER:
  A logging.Logger instance that extensions can use
* MessageFormat:
  An enum of kinds of messages that an extension might return.
* TaskFunction:
  A type alias for the function signature of the trappedbot_task function extensions must implement.
* TaskMessageContext:
  An argument passed to the TaskFunction that extensions must implement.
* TaskResult:
  The return value for the TaskFunction that extensions must implement.
* version_cute():
  Return an on-brand bot version string
* version_raw():
  Return a bare bot version string
"""

from trappedbot import appconfig
from trappedbot.applogger import LOGGER
from trappedbot.mxutil import MessageFormat
from trappedbot.tasks.task import TaskFunction, TaskMessageContext, TaskResult
from trappedbot.version import version_cute, version_raw

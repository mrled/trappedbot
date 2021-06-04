"""The trappedbot extensions namespace

Things in this namespace are guaranteed not to change between major version.
"""

from trappedbot import LOGGER, version_cute, version_raw
from trappedbot.mxutil import MessageFormat
from trappedbot.tasks.task import TaskMessageContext, TaskResult
from trappedbot.extensions.internal import appconfig_extension

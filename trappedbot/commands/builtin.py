"""Built-in commands

These commands override any that are defined in the config
"""

from trappedbot.commands.command import Command
from trappedbot.tasks.builtin import BUILTIN_TASKS


BUILTIN_COMMANDS = {
    "help": Command(
        "help", BUILTIN_TASKS["help"], help="Show bot help", allow_untrusted=True
    ),
    "version": Command(
        "version",
        BUILTIN_TASKS["version"],
        help="Show bot version",
        allow_untrusted=True,
    ),
}

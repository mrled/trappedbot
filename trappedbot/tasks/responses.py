"""Free text responses by the bot"""

import re
import typing


class Response(typing.NamedTuple):
    """If an incoming message matches the .regex, respond with the .message"""

    regex: re.Pattern
    message: str

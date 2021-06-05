"""Response list
"""

import re
import typing

from trappedbot.applogger import LOGGER
from trappedbot.responses.response import Response


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
            LOGGER.critical(
                f"Failed to compile regex {regex_str} for response definition found at index {idx} with exception {exc}, ignoring..."
            )
            return None
        return Response(regex, yamlobj["response"])
    except BaseException:
        LOGGER.critical(
            f"Invalid response definition found at index {idx}, ignoring..."
        )
        return None


def yamlobj2rsplist(responses_yaml_obj: typing.Any) -> typing.List[Response]:
    """Return a ResponseList from a yaml object"""
    responses: typing.List[Response] = []
    for idx, rdefn in enumerate(responses_yaml_obj):
        if (response := yamlobj2response(idx, rdefn)) :
            responses.append(response)
    return responses

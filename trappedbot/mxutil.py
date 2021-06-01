"""Matrix utilities for trappedbot"""

import re


class InvalidMxidError(ValueError):
    """An invalid Matrix ID (mxid)"""

    def __init__(self, mxid):
        self.mxid = mxid

    def __str__(self):
        return f"Invalid mxid '{self.mxid}'"


class Mxid(object):
    def __init__(self, user: str, homeserver: str):
        self.user = user
        self.homeserver = homeserver

    @property
    def mxid(self):
        return f"@{self.user}:{self.homeserver}"

    @classmethod
    def fromstr(cls, mxid: str) -> "Mxid":
        m = re.match(r"\@([a-zA-Z0-9-_]+)\:([a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+)$", mxid)
        if not m:
            raise InvalidMxidError(mxid)
        username = m.group(1)
        homeserver = m.group(2)
        if not username or not homeserver:
            raise InvalidMxidError(mxid)
        return Mxid(username, homeserver)
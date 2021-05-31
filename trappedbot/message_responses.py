#!/usr/bin/env python3

"""Respond to chat messages
"""

from nio import AsyncClient
from nio.rooms import MatrixRoom
from nio.events.room_events import RoomMessageText

from trappedbot.chat_functions import send_text_to_room
from trappedbot.config import Config
from trappedbot.storage import Storage


class Message(object):
    """Process messages."""

    def __init__(
        self,
        client: AsyncClient,
        store: Storage,
        config: Config,
        message_content: str,
        room: MatrixRoom,
        event: RoomMessageText,
    ):
        """Initialize a new Message.

        Arguments:
            client: nio client used to interact with matrix
            store: Bot storage
            config: Bot configuration parameters
            message_content: The body of the message
            room: The room the event came from
            event: The event defining the message
        """
        self.client = client
        self.store = store
        self.config = config
        self.message_content = message_content
        self.room = room
        self.event = event

    async def process(self):
        """Process and possibly respond to the message."""
        if self.message_content.lower() == "hello world":
            await self._hello_world()

    async def _hello_world(self):
        await send_text_to_room(
            self.client, self.room.room_id, "Trapped in a Matrix server, send help!"
        )

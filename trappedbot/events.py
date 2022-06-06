"""Events inside TrappedBot itself"""


import typing

from nio import AsyncClient

from trappedbot.applogger import LOGGER


class EventNotifyAction():
    """An action to notify a room in response to a TrappedBot event"""

    def __init__(self, event: str, room: str, message: str):
        self.event = event
        self.room = room
        self.message = message

    async def __call__(self, client: AsyncClient):
        LOGGER.info(f"Running notify action for {self.event}: {self.room}: {self.message}")
        result = await client.room_send(
            room_id=self.room,
            message_type="m.room.message",
            content={"messagetype": "m.text", "body": self.message}
        )
        return result

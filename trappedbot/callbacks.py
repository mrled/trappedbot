"""Implement callbacks for:

- receiving a text message
- receiving an invite
- performing an emoji verification (bot must run in forground as keyboard input is required)
"""

import traceback

from nio import (
    JoinError,
    KeyVerificationStart,
    KeyVerificationCancel,
    KeyVerificationKey,
    KeyVerificationMac,
    ToDeviceError,
    LocalProtocolError,
)
from nio.rooms import MatrixRoom
from nio.events.room_events import RoomMessageText

import trappedbot
from trappedbot.commands import Command
from trappedbot.tasks.builtin import BUILTIN_TASKS
from trappedbot.tasks.taskdefinition import TaskDefinition


# TODO: Consider NOT logging message contents unless passing some kind of --really-log-messages flag or something
def msglog(logline: str, room: MatrixRoom, event: RoomMessageText):
    """Log a line with room name/user/message metadata"""
    trappedbot.LOGGER.debug(
        f"{logline} % {room.display_name} | {room.user_name(event.sender)}: {event.body}"
    )


def in_dms(room: MatrixRoom) -> bool:
    """Are we in DMs, or in a larger room?

    TODO: is there a better way to determine this?
    """
    # room.is_group is often a DM, but not always.
    # room.is_group does not allow room aliases
    # room.member_count > 2 ... we assume a public room
    # room.member_count <= 2 ... we assume a DM
    return room.member_count <= 2


class Callbacks(object):
    """Collection of all callbacks."""

    def __init__(self, client, store):
        """Initialize.

        Arguments:
        ---------
            client (nio.AsyncClient): nio client used to interact with matrix
            store (Storage): Bot storage
        """
        self.client = client
        self.store = store
        self.taskdict = TaskDefinition(trappedbot.APPCONFIG.task_dict_filepath)
        if len(self.taskdict.tasks) == 0:
            trappedbot.LOGGER.info(
                f"No tasks defined in task definition file, using builtins"
            )
            for task in BUILTIN_TASKS:
                self.taskdict.tasks[task.name] = task
        self.command_prefix = trappedbot.APPCONFIG.command_prefix

    async def message(self, room, event):
        """Handle an incoming message event.

        Arguments:
        ---------
            room (nio.rooms.MatrixRoom): The room the event came from
            event (nio.events.room_events.RoomMessageText): The event
                defining the message

        """

        if event.body.startswith(self.command_prefix):
            has_command_prefix = True
            msg = event.body[len(self.command_prefix) :]
        else:
            has_command_prefix = False
            msg = event.body

        if event.sender == self.client.user:
            msglog("Ignoring message from myself", room, event)
            return
        elif not has_command_prefix and not in_dms(room):
            msglog("Ignoring message without prefix in multi-user room", room, event)
            return
        else:
            msglog("Handling message", room, event)

        command = Command(self.client, self.store, self.taskdict, msg, room, event)
        await command.process()

    async def invite(self, room, event):
        """Handle an incoming invite event.

        If an invite is received, then join the room specified in the invite.
        """
        trappedbot.LOGGER.debug(f"Got invite to {room.room_id} from {event.sender}.")

        # Attempt to join 3 times before giving up
        for attempt in range(3):
            result = await self.client.join(room.room_id)
            if type(result) == JoinError:
                trappedbot.LOGGER.error(
                    f"Error joining room {room.room_id} (attempt %d): %s",
                    attempt,
                    result.message,
                )
            else:
                break
        else:
            trappedbot.LOGGER.error("Unable to join room: %s", room.room_id)

        # Successfully joined room
        trappedbot.LOGGER.info(f"Joined {room.room_id}")

    async def to_device_cb(self, event):  # noqa
        """Handle events sent to device.

        Specifically this will perform Emoji verification.
        It will accept an incoming Emoji verification requests
        and follow the verification protocol.
        """
        try:
            client = self.client
            trappedbot.LOGGER.debug(
                f"Device Event of type {type(event)} received in " "to_device_cb()."
            )

            if isinstance(event, KeyVerificationStart):  # first step
                """first step: receive KeyVerificationStart
                KeyVerificationStart(
                    source={'content':
                            {'method': 'm.sas.v1',
                             'from_device': 'DEVICEIDXY',
                             'key_agreement_protocols':
                                ['curve25519-hkdf-sha256', 'curve25519'],
                             'hashes': ['sha256'],
                             'message_authentication_codes':
                                ['hkdf-hmac-sha256', 'hmac-sha256'],
                             'short_authentication_string':
                                ['decimal', 'emoji'],
                             'transaction_id': 'SomeTxId'
                             },
                            'type': 'm.key.verification.start',
                            'sender': '@user2:example.org'
                            },
                    sender='@user2:example.org',
                    transaction_id='SomeTxId',
                    from_device='DEVICEIDXY',
                    method='m.sas.v1',
                    key_agreement_protocols=[
                        'curve25519-hkdf-sha256', 'curve25519'],
                    hashes=['sha256'],
                    message_authentication_codes=[
                        'hkdf-hmac-sha256', 'hmac-sha256'],
                    short_authentication_string=['decimal', 'emoji'])
                """

                if "emoji" not in event.short_authentication_string:
                    estr = (
                        "Other device does not support emoji verification "
                        f"{event.short_authentication_string}. Aborting."
                    )
                    print(estr)
                    trappedbot.LOGGER.info(estr)
                    return
                resp = await client.accept_key_verification(event.transaction_id)
                if isinstance(resp, ToDeviceError):
                    estr = f"accept_key_verification() failed with {resp}"
                    print(estr)
                    trappedbot.LOGGER.info(estr)

                sas = client.key_verifications[event.transaction_id]

                todevice_msg = sas.share_key()
                resp = await client.to_device(todevice_msg)
                if isinstance(resp, ToDeviceError):
                    estr = f"to_device() failed with {resp}"
                    print(estr)
                    trappedbot.LOGGER.info(estr)

            elif isinstance(event, KeyVerificationCancel):  # anytime
                """at any time: receive KeyVerificationCancel
                KeyVerificationCancel(source={
                    'content': {'code': 'm.mismatched_sas',
                                'reason': 'Mismatched authentication string',
                                'transaction_id': 'SomeTxId'},
                    'type': 'm.key.verification.cancel',
                    'sender': '@user2:example.org'},
                    sender='@user2:example.org',
                    transaction_id='SomeTxId',
                    code='m.mismatched_sas',
                    reason='Mismatched short authentication string')
                """

                # There is no need to issue a
                # client.cancel_key_verification(tx_id, reject=False)
                # here. The SAS flow is already cancelled.
                # We only need to inform the user.
                estr = (
                    f"Verification has been cancelled by {event.sender} "
                    f'for reason "{event.reason}".'
                )
                print(estr)
                trappedbot.LOGGER.info(estr)

            elif isinstance(event, KeyVerificationKey):  # second step
                """Second step is to receive KeyVerificationKey
                KeyVerificationKey(
                    source={'content': {
                            'key': 'SomeCryptoKey',
                            'transaction_id': 'SomeTxId'},
                        'type': 'm.key.verification.key',
                        'sender': '@user2:example.org'
                    },
                    sender='@user2:example.org',
                    transaction_id='SomeTxId',
                    key='SomeCryptoKey')
                """
                sas = client.key_verifications[event.transaction_id]

                print(f"{sas.get_emoji()}")
                # don't log the emojis

                # The bot process must run in forground with a screen and
                # keyboard so that user can accept/reject via keyboard.
                # For emoji verification bot must not run as service or
                # in background.
                yn = input("Do the emojis match? (Y/N) (C for Cancel) ")
                if yn.lower() == "y":
                    estr = (
                        "Match! The verification for this " "device will be accepted."
                    )
                    print(estr)
                    trappedbot.LOGGER.info(estr)
                    resp = await client.confirm_short_auth_string(event.transaction_id)
                    if isinstance(resp, ToDeviceError):
                        estr = "confirm_short_auth_string() " f"failed with {resp}"
                        print(estr)
                        trappedbot.LOGGER.info(estr)
                elif yn.lower() == "n":  # no, don't match, reject
                    estr = (
                        "No match! Device will NOT be verified "
                        "by rejecting verification."
                    )
                    print(estr)
                    trappedbot.LOGGER.info(estr)
                    resp = await client.cancel_key_verification(
                        event.transaction_id, reject=True
                    )
                    if isinstance(resp, ToDeviceError):
                        estr = f"cancel_key_verification failed with {resp}"
                        print(estr)
                        trappedbot.LOGGER.info(estr)
                else:  # C or anything for cancel
                    estr = "Cancelled by user! Verification will be " "cancelled."
                    print(estr)
                    trappedbot.LOGGER.info(estr)
                    resp = await client.cancel_key_verification(
                        event.transaction_id, reject=False
                    )
                    if isinstance(resp, ToDeviceError):
                        estr = f"cancel_key_verification failed with {resp}"
                        print(estr)
                        trappedbot.LOGGER.info(estr)

            elif isinstance(event, KeyVerificationMac):  # third step
                """Third step is to receive KeyVerificationMac
                KeyVerificationMac(
                    source={'content': {
                        'mac': {'ed25519:DEVICEIDXY': 'SomeKey1',
                                'ed25519:SomeKey2': 'SomeKey3'},
                        'keys': 'SomeCryptoKey4',
                        'transaction_id': 'SomeTxId'},
                        'type': 'm.key.verification.mac',
                        'sender': '@user2:example.org'},
                    sender='@user2:example.org',
                    transaction_id='SomeTxId',
                    mac={'ed25519:DEVICEIDXY': 'SomeKey1',
                         'ed25519:SomeKey2': 'SomeKey3'},
                    keys='SomeCryptoKey4')
                """
                sas = client.key_verifications[event.transaction_id]
                try:
                    todevice_msg = sas.get_mac()
                except LocalProtocolError as e:
                    # e.g. it might have been cancelled by ourselves
                    estr = (
                        f"Cancelled or protocol error: Reason: {e}.\n"
                        f"Verification with {event.sender} not concluded. "
                        "Try again?"
                    )
                    print(estr)
                    trappedbot.LOGGER.info(estr)
                else:
                    resp = await client.to_device(todevice_msg)
                    if isinstance(resp, ToDeviceError):
                        estr = f"to_device failed with {resp}"
                        print(estr)
                        trappedbot.LOGGER.info(estr)
                    estr = (
                        f"sas.we_started_it = {sas.we_started_it}\n"
                        f"sas.sas_accepted = {sas.sas_accepted}\n"
                        f"sas.canceled = {sas.canceled}\n"
                        f"sas.timed_out = {sas.timed_out}\n"
                        f"sas.verified = {sas.verified}\n"
                        f"sas.verified_devices = {sas.verified_devices}\n"
                    )
                    print(estr)
                    trappedbot.LOGGER.info(estr)
                    estr = (
                        "Emoji verification was successful!\n"
                        "Initiate another Emoji verification from "
                        "another device or room if desired. "
                        "Or if done verifying, hit Control-C to stop the "
                        "bot in order to restart it as a service or to "
                        "run it in the background."
                    )
                    print(estr)
                    trappedbot.LOGGER.info(estr)
            else:
                estr = (
                    f"Received unexpected event type {type(event)}. "
                    f"Event is {event}. Event will be ignored."
                )
                print(estr)
                trappedbot.LOGGER.info(estr)
        except BaseException:
            estr = traceback.format_exc()
            print(estr)
            trappedbot.LOGGER.info(estr)

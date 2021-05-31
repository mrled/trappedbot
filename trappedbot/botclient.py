"""The bot client
"""

from time import sleep

from nio import (
    AsyncClient,
    AsyncClientConfig,
    RoomMessageText,
    InviteMemberEvent,
    LoginError,
    LocalProtocolError,
    UpdateDeviceError,
    KeyVerificationEvent,
)
from aiohttp import ServerDisconnectedError, ClientConnectionError

import trappedbot
from trappedbot.callbacks import Callbacks
from trappedbot.config import Config
from trappedbot.storage import Storage


async def bot(configpath: str):
    """The bot client itself"""

    config = Config(configpath)
    store = Storage(config.database_filepath)

    client_config = AsyncClientConfig(
        max_limit_exceeded=0,
        max_timeouts=0,
        store_sync_tokens=True,
        encryption_enabled=True,
    )

    client = AsyncClient(
        config.homeserver_url,
        config.user_id,
        device_id=config.device_id,
        store_path=config.store_filepath,
        config=client_config,
    )

    callbacks = Callbacks(client, store, config)
    client.add_event_callback(callbacks.message, (RoomMessageText,))
    client.add_event_callback(callbacks.invite, (InviteMemberEvent,))
    client.add_to_device_callback(callbacks.to_device_cb, (KeyVerificationEvent,))

    while True:
        try:
            try:
                if config.access_token:
                    trappedbot.LOGGER.debug(
                        "Using access token from config file to log in."
                    )
                    client.restore_login(
                        user_id=config.user_id,
                        device_id=config.device_id,
                        access_token=config.access_token,
                    )

                else:
                    trappedbot.LOGGER.debug(
                        "Using password from config file to log in."
                    )
                    login_response = await client.login(
                        password=config.user_password,
                        device_name=config.device_name,
                    )

                    # Check if login failed
                    if type(login_response) == LoginError:
                        trappedbot.LOGGER.error(
                            "Failed to login: " f"{login_response.message}"
                        )
                        return False
                    trappedbot.LOGGER.info(
                        (
                            f"access_token of device {config.device_name}"
                            f' is: "{login_response.access_token}"'
                        )
                    )

            except LocalProtocolError as exc:
                # There's an edge case here where the user hasn't installed
                # the correct C dependencies. In that case, a
                # LocalProtocolError is raised on login.
                trappedbot.LOGGER.fatal(
                    "Failed to login. "
                    "Have you installed the correct dependencies? "
                    "https://github.com/poljar/matrix-nio#installation "
                    f"Error: {exc}",
                )
                return False

            trappedbot.LOGGER.debug(
                f"Logged in successfully as user {config.user_id} "
                f"with device {config.device_id}."
            )

            # Sync encryption keys with the server
            # Required for participating in encrypted rooms
            if client.should_upload_keys:
                await client.keys_upload()

            if config.change_device_name:
                content = {"display_name": config.device_name}
                resp = await client.update_device(config.device_id, content)
                if isinstance(resp, UpdateDeviceError):
                    trappedbot.LOGGER.debug(f"update_device failed with {resp}")
                else:
                    trappedbot.LOGGER.debug(f"update_device successful with {resp}")

            if config.trust_own_devices:
                await client.sync(timeout=30000, full_state=True)
                # Trust your own devices automatically.
                # Log it so it can be manually checked
                for device_id, olm_device in client.device_store[
                    config.user_id
                ].items():
                    trappedbot.LOGGER.debug(
                        "My other devices are: "
                        f"device_id={device_id}, "
                        f"olm_device={olm_device}."
                    )
                    trappedbot.LOGGER.info(
                        "Setting up trust for my own "
                        f"device {device_id} and session key "
                        f"{olm_device.keys['ed25519']}."
                    )
                    client.verify_device(olm_device)

            await client.sync_forever(timeout=30000, full_state=True)

        except (ClientConnectionError, ServerDisconnectedError):
            trappedbot.LOGGER.warning(
                "Unable to connect to homeserver, retrying in 15s..."
            )

            # Sleep so we don't bombard the server with login requests
            sleep(15)
        finally:
            # Make sure to close the client connection on disconnect
            await client.close()

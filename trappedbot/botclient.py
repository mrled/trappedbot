"""The bot client.
"""

from time import sleep

from nio import (
    AsyncClient,
    AsyncClientConfig,
    RoomMessage,
    RoomMessageText,
    InviteMemberEvent,
    LoginError,
    LocalProtocolError,
    UpdateDeviceError,
    KeyVerificationEvent,
)
from aiohttp import ServerDisconnectedError, ClientConnectionError

from trappedbot import appconfig
from trappedbot.applogger import LOGGER
from trappedbot.callbacks import Callbacks
from trappedbot.storage import Storage


async def botloop():
    """The bot client itself.

    Execute an infinite loop, read the app configuration, and listen for Matrix events.

    Creates a `nio.AsyncClient` and adds callbacks with
    `nio.AsyncClient.add_event_callback` and
    `nio.AsyncClient.add_to_device_callback`.

    See the callbacks we define in `trappedbot.callbacks`.

    If the application has not been configured before this function runs,
    the bot will not have credentials to connect to the Matrix homeserver,
    and will exit.
    """

    config = appconfig.get()
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

    callbacks = Callbacks(client, store)
    client.add_event_callback(callbacks.message, (RoomMessage, RoomMessageText,))
    client.add_event_callback(callbacks.invite, (InviteMemberEvent,))
    client.add_to_device_callback(callbacks.to_device_cb, (KeyVerificationEvent,))

    while True:
        try:
            try:
                if config.user_access_token:
                    LOGGER.debug("Using access token from config file to log in.")
                    client.restore_login(
                        user_id=config.user_id,
                        device_id=config.device_id,
                        access_token=config.user_access_token,
                    )

                else:
                    LOGGER.debug("Using password from config file to log in.")
                    login_response = await client.login(
                        password=config.user_password,
                        device_name=config.device_name,
                    )

                    # Check if login failed
                    if type(login_response) == LoginError:
                        LOGGER.error("Failed to login: " f"{login_response.message}")
                        return False
                    LOGGER.debug(
                        f'access_token of device {config.device_name} is: "{login_response.access_token}"'
                    )
                    LOGGER.debug(f"Full login_response: {login_response}")

            except LocalProtocolError as exc:
                # There's an edge case here where the user hasn't installed
                # the correct C dependencies. In that case, a
                # LocalProtocolError is raised on login.
                LOGGER.critical(
                    "Failed to login. "
                    "Have you installed the correct dependencies? "
                    "https://github.com/poljar/matrix-nio#installation "
                    f"Error: {exc}",
                )
                return False

            LOGGER.debug(
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
                    LOGGER.critical(f"update_device failed with {resp}")
                else:
                    LOGGER.debug(f"update_device successful with {resp}")

            if config.trust_own_devices:
                await client.sync(timeout=30000, full_state=True)
                # Trust your own devices automatically.
                # Log it so it can be manually checked
                for device_id, olm_device in client.device_store[
                    config.user_id
                ].items():
                    LOGGER.info(
                        f"My other devices are: device_id={device_id}, olm_device={olm_device}."
                    )
                    LOGGER.info(
                        f"Setting up trust for my own device {device_id} and session key {olm_device.keys['ed25519']}."
                    )
                    client.verify_device(olm_device)

            LOGGER.info("Running actions for 'botstartup' event, if any...")
            botstartup = config.events.get('botstartup', None)
            if botstartup:
                await botstartup(client)

            LOGGER.info("Running nio AsyncClient.sync_forever()...")
            # await client.sync_forever(timeout=30000, full_state=True)
            await client.sync_forever(timeout=30000)

        except (ClientConnectionError, ServerDisconnectedError):
            LOGGER.warning("Unable to connect to homeserver, retrying in 15s...")

            # Sleep so we don't bombard the server with login requests
            sleep(15)
        finally:
            # Make sure to close the client connection on disconnect
            await client.close()

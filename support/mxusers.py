"""Get Matrix users connected to a given homeserver

This is written as a proof of concept and a starter for third party extensions,
but take care. It can cause load on the Matrix homeserver, and you may not want
to expose your homeserver's admin API to the Internet.

In its current form, it's definitely not suitable for large or even medium
homeservers.
"""

import typing

import requests

from trappedbot.extensions import (
    LOGGER,
    MessageFormat,
    TaskMessageContext,
    TaskResult,
    appconfig,
)


def is_bridged_user(username: str):
    """Return true if the username represents a bridged user

    This is just heuristicly done based on bridges I run myself;
    it will require tweaking for other cases
    """
    if username.startswith("@_slackpuppet"):
        return True
    if username.startswith("@hbirc_"):
        return True
    if username.startswith("@_discordpuppet"):
        return True
    return False


def get_mx_users(homeserver: str, bearertoken: str) -> typing.Dict:
    """Get a list of Matrix users connected to a homeserver

    homeserver:     A homeserver, e.g. matrix.example.com
    bearertoken:    A bearer token with administrative privileges to the server

    The API responds with objects like:
        {
            "users": [
                {
                    "name": "@hbirc_oftc_alxndr:micahrl.com",
                    "user_type": null,
                    "is_guest": 0,
                    "admin": 0,
                    "deactivated": 0,
                    "shadow_banned": false,
                    "displayname": "alxndr",
                    "avatar_url": null
                }
                //...
            ],
        "total": 1356, // Total number of users
        "next_token": 100 // Do &from=100 to get the next batch of users
    """
    uri = f"{homeserver}/_synapse/admin/v2/users"
    params = {"from": "0", "limit": "100", "guests": "false"}
    headers = {
        "Authorization": f"Bearer {bearertoken}",
    }
    response = requests.get(uri, params=params, headers=headers)
    LOGGER.debug(
        f"Got response from server: uri {response.url} code {response.status_code} text: {response.text}"
    )
    jresponse = response.json()
    users = jresponse["users"]
    while "next_token" in jresponse:
        params["from"] = jresponse["next_token"]
        response = requests.get(uri, params=params, headers=headers)
        jresponse = response.json()
        users += jresponse["users"]
    # trappedbot.LOGGER.debug(f"Got JSON response from Matrix server: {jresponse}")
    return users


def get_mx_users_wrapper(
    _arguments: typing.List[str], _context: TaskMessageContext
) -> TaskResult:
    """A TaskFunction-compatible wrapper script for get_mx_users

    Required extension configuration configuration:
        extension:
            get_mx_users:
                homeserver: https://matrix.example.edu  # May be different from bot's homeserver
                bearer_token: VERY_LONG_TOKEN_HERE      # Must have admin privileges

    You can use 'trappedbot access-token' to retrieve an access token.

    Note that the Matrix server's admin API may not have been enabled during installation.
    E.g. the matrix-docker-ansible-deploy project disabled is by default.
    matrix_nginx_proxy_proxy_matrix_client_api_forwarded_location_synapse_admin_api_enabled
    https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/roles/matrix-nginx-proxy/defaults/main.yml
    """
    config = appconfig.get()
    homeserver = config.extension("get_mx_users", "homeserver")
    bearer_token = config.extension("get_mx_users", "bearer_token")
    userlist = get_mx_users(homeserver, bearer_token)

    # WARNING: with bridging, these user counts are way too high,
    # and the message doesn't even show up
    # (though the bot does try to send it).
    # We filter out bridged users with this dumb hack:
    filtered_userlist = [u for u in userlist if not is_bridged_user(u["name"])]

    table = "<table>"
    table += "<tr><th>Display name</th><th>MXID</th><th>Type</th><th>Admin</th></tr>"
    for user in filtered_userlist:
        table += f"<tr><th>{user['displayname']}</th><td>{user['name']}</td><td>{user['user_type']}</td><td>{user['admin']}</td></tr>"
    table += "</table>"
    return TaskResult(table, MessageFormat.FORMATTED)

    # return TaskResult(
    #     "\n".join([f"- {u['name']}" for u in filtered_userlist]), MessageFormat.MARKDOWN
    # )


trappedbot_task = get_mx_users_wrapper

"""Trapped in a Matrix server, send help!

This is the implementation of a tiny daemon (in the spiritual, but also computer, sense) which we can trap inside our Matrix servers to perform tasks for us.

* Project page: <https://github.com/mrled/trappedbot>
* Online documentation: <https://pages.micahrl.com/trappedbot>

trappedbot can be configured to do a few things:

* Listen for a command prefix, receive a command, and run a task. For instance:

        @you:example.com |   !trappedbot version
        @bot:example.com |   Trapped in a Matrix server, send help! Version 0.9.0

* Listen for phrases to be used in chat, and respond to them, without a command prefix. For instance:

        @you:example.com |   im hungry
        @bot:example.com |   Replying to @you:example.com:
                             > im hungry
                             Hi hungry, I'm dad!

As you can see, these are the type of features it is vital to have in a channel of importance or prestige.

## Configuring trappedbot

See the configuration file example on GitHub: <https://github.com/mrled/trappedbot/blob/master/trappedbot.config.yml>

## Extending trappedbot

You can write Python modules that extend trappedbot. See the `trappedbot.extensions` module.

## Running the trappedbot command

The bot has a few useful subcommands that you can access via the built-in help:

    > trappedbot --help
    usage: trappedbot [-h] [--debug] [--verbose] {version,bot,builtin-tasks,access-token} ...

    Trapped in a Matrix server, send help!

    positional arguments:
    {version,bot,builtin-tasks,access-token}
        version             Show version
        bot                 Start the bot
        builtin-tasks       List built in tasks
        access-token        Get an access token from a Matrix server

    optional arguments:
    -h, --help            show this help message and exit
    --debug, -d           Include verbose/debug messages, and enter the debugger on unhandled exceptions
    --verbose, -v         Include verbose/debug messages

## Running the bot in production

While simply running `trappedbot bot /path/to/config.yml` will start the bot, it is recommended that you run it as a service on your operating system. If your system is a Linux system that runs systemd, you may wish to write a systemd service definition file.

* Example systemd service definition file: <https://github.com/mrled/trappedbot/blob/master/support/trappedbot.service>

Once you customize that file for your use case, you might install it like so:

* Copy it to somewhere like `/etc/systemd/system/trappedbot.service`
* Reload the systemd daemon with `sudo systemctl daemon-reload`
* Start the bot with `sudo systemctl start trappedbot`
* Automatically run it every time your host boots with `sudo systemctl enable trappedbot`
* View the logs with `sudo journalctl -fu trappedbot`

"""

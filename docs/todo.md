# To do

* Features
    * Allow responding with emoji responses
    * Hot-reload when the bot files or configuration change on disk
        * [watchdog](https://pypi.org/project/watchdog/): polling only
        * [watchgod](https://pypi.org/project/watchgod/): polling only, claims to improve on watchdog
        * [fswatch](https://github.com/emcrisostomo/fswatch): supports kernel monitors/notifications like fsevents and inotify, but there are significant per-platform limitations from the underlying APIs.
    * Log some events to a specified channel. Thinking especially for automatic hot reloads.
    * Add an RSS reader that polls for changes to feeds and posts them to a channel
        * This is a new type of thing - it's not a bot command, but some background behavior it can notify you on
        * This could be especially useful because it is a way to push notifications to your phone
    * Discord server -style auto invites to rooms based on emoji reactions to messages in a given room
    * That thing where MSCHF did a Slack server with all of The Office
        * Long, familiar stuff like The Office, Friends, etc, is nice because you can put it on in the background and enjoy it without paying too much attention
        * For novel stuff, something very short is probably better, perhaps Made Out Of Meat
    * That makes me want to implement a game with Matrix bots
    * Do not allow setting paths in task definition
        * Make the user do this in the env before starting the bot, or specify full paths to executables
    * Don't ask users to care about change_device_name.
    * Have 'help commands' be different from 'help responses'
    * Allow text responses only in specific rooms
    * Builtin tasks should be able to have separate names, e.g. 'builtin: echo' not 'echo: builtin: yes'
    * I have config.commands.commands['cmdname'] (and similar for responses); make this look nicer
    * Fix bot help - it shows "no help is available" for all tasks except builtin ones
    * Clean up bot help output. Possibly with markdown, possibly in a table.
    * Add a command to list all responses.
* Docs
    * Some of the old scripts were just docs placeholders for the user to write a real implementation, e.g. `backup.sh`; write docs instead?
    * Publish somewhere like readthedocs or github pages?
* Publish to pypi
* Offer PRs for anything the eno project is interested in?

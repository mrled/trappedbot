# To do

* Features
    * Allow responding to non-targetted messages, e.g. `Jesus Christ` -> `Yes, my son?`
    * Allow responding with emoji responses
    * Allow user-defined Python functions
    * Hot-reload when the bot files or configuration change on disk, maybe using pyinotify
    * Log some events to a specified channel. Thinking especially for automatic hot reloads.
    * Add an RSS reader that polls for changes to feeds and posts them to a channel
        * This is a new type of thing - it's not a bot command, but some background behavior it can notify you on
        * This could be especially useful because it is a way to push notifications to your phone
    * Discord server -style auto invites to rooms based on emoji reactions to messages in a given room
    * That thing where MSCHF did a Slack server with all of The Office
        * Long, familiar stuff like The Office, Friends, etc, is nice because you can put it on in the background and enjoy it without paying too much attention
        * For novel stuff, something very short is probably better, perhaps Made Out Of Meat
    * That makes me want to implement a game with Matrix bots
    * Provide stable API for external extensions
        * Make this API small and manageable and expose it through some interface like `trappedbot.extensions.*`
        * E.g. Task and related stuff could be re-exported from there
        * Users can use anything in the codebase but not promised to work between versions
    * Make systemcmds always output CODE, and then you don't have to define format in task defn file
* Docs
    * Some of the old scripts were just docs placeholders for the user to write a real implementation, e.g. `backup.sh`; write docs instead?
    * Publish somewhere like readthedocs or github pages?
* Publish to pypi
* Offer PRs for anything the eno project is interested in?

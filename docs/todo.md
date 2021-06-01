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
* Docs
    * Some of the old scripts were just docs placeholders for the user to write a real implementation, e.g. `backup.sh`; write docs instead?
    * Publish somewhere like readthedocs or github pages?
* Publish to pypi
* Offer PRs for anything the eno project is interested in?

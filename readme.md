# Trapped in a Matrix server, send help!

This is the implementation of a tiny daemon (in the spiritual, but also computer, sense) which we can trap inside our Matrix servers to perform tasks for us.

## Requirements

* `libolm` is required by `matrix-nio[e2e]` for end-to-end encryption support
    * <https://gitlab.matrix.org/matrix-org/olm>
    * On Debian-derived systems, including Ubuntu, `apt-get install libolm-dev`

## Local development

API documentation (generated from source code) is available at
<https://pages.micahrl.com/trappedbot>

Set up an 'editable' environment:

```sh
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip # optional
pip install build mypy black types-PyYAML
pip install -e .
```

If you have libolm installed in a nonstandard path, you can run the `pip install` with instructions on where to find them. For instance, with a nonstandard Homebrew installation:

```sh
export HOMEBREWDIR=/usr/local/opt/nonstandard/location/for/homebrew
export CFLAGS="-I$HOMEBREWDIR/include -L$HOMEBREWDIR/lib"
pip install -e .
```

Build distributable packages:

```sh
python -m build
```

Run it:

```sh
trappedbot -h
```

If your libraries are installed to strange locations, you may need to modify your venv's `lib/python3.9/site-packages/magic/loader.py` so that it adds your snowflake location to its list of paths. Here's how I did mine:

```python
def _lib_candidates():

  yield find_library('magic')

  if sys.platform == 'darwin':

    paths = [
      '/opt/local/lib',
      '/usr/local/lib',
      '/opt/homebrew/lib',
      '/Users/mrled/opt/homebrew/lib',                      #### I added this line
    ] + glob.glob('/usr/local/Cellar/libmagic/*/lib')

#...
```

Is that a bad hack??? Sure! Presumably if you're an an OS with a sane package manager this is not a problem.
(Via: <https://github.com/ahupp/python-magic/issues/238#issuecomment-789287147>)

Generating the docs:

```sh
pdoc --html trappedbot
cd html/trappedbot
python3 -m http.server
# And then browse to http://localhost:8000 to view them
```

## Running in production

* Install non-python [prerequisites](#requirements)
* Create a Unix user for the bot and su to it
* Install trappedbot, e.g. `python3 -m pip install --user trappedbot`
* See the [systemd service definition file example](support/trappedbot.service) for how to run this under systemd.

## Configuration

See the [example configuration file](trappedbot.config.yml) for an example

This file configures credentials and so forth, and also the commands and responses that your bot is capable of.

## Extensions

You can write custom extensions for `trappedbot` in Python.

The package exports the `trappedbot.extensions` namespace, which contains interfaces that are guaranteed not to change between major versions. You are welcome to use anything else internal, but implementations may change in minor releases.

Extensions must export a `trappedbot_task` function of the type `trappedbot.tasks.task.TaskFunction`.

See the documentation at <https://pages.micahrl.com/trappedbot/extensions/>

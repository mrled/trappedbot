# Trapped in a Matrix server, send help!

This is the implementation of a tiny daemon (in the spiritual, but also computer, sense) which we can trap inside our Matrix servers to perform tasks for us.

## Requirements

* `libolm` is required by `matrix-nio[e2e]` for end-to-end encryption support
    * <https://gitlab.matrix.org/matrix-org/olm>
    * On Debian-derived systems, including Ubuntu, `apt-get install libolm-dev`

## Local development

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

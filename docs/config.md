Configuration
===

This is a list of configuration options for the various config files involved with sshchan.

How to access and change config options
---
Use the `admin.py` script with the following commands:
* `lsconfig` lists current configuration options.
* `config` changes the values of configuration options.
Type in the `h` command to read more about those commands.

What the options are
---
### `display_legacy`
Options are `True` and `False`. If `True`, the old, command-line interface is used. If `False`, the very experimental and currently unfinished
urwid GUI is used instead.

### `motd_path`
The path to the file whose contents will be displayed as the Message of the Day. This appears at the top of the window when users first connect.

### `name`
A string which is printed in the 'NAME' field on the sshchan homescreen.

### `rootdir`
The root directory of the chan, i.e. where all the boards lie within. This is normally set during initialisation (see `docs/setup.md`).

### `version`
The version of sshchan that you are using. This is set during initialisation. It would be wise not to change it.

sshchan-setup
===

Usage
---
Initialisation (setting up sshchan for the first time):
`bash setup.sh`

Administration (changing configuration, adding/removing boards, etc.):
`python3 gui.py -admin`

Initialisation
---
Initialisation is done with the module `init.py`. It has two commands:
### `init.py init_tempconf`
This will create a temporary config file in the current directory. It will set the `rootdir` and `version` values.

### `init.py init`
Once the file `/etc/sshchan.conf` has been created, this will read it for the `rootdir` value and set up all the required stuff in the specified directory.

Administration
---
This can be done from the `gui.py` module with the option `-admin`.

### `add [board name] [board description]`
Adds the board to your boardlist and creates the needed directories and files. NOTE: Every character after the board name will become part of the description. There is no need to add inverted commas.
e.g.
	add a Animu and Mango
	add tech Technology
etc.

### `del [board name]`
Removes the specified board name (without slashes) from the boardlist.

### `rename [board name] [new description]`
Changes the specified board's description to [new description]. 

### `config [config option] [value]`
Sets the value of [config option] to [value] in `/etc/sshchan.conf`. See `docs/config.md` for a list of config options.

### `list`
Lists all the current boards.

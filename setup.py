#!/usr/bin/env python3
"""
Setup script to create everything needed for a working textboard.

Copyright (c) 2015 makos <https://github.com/makos>
under GNU GPL v3, see LICENSE for details
"""

import json
import sys
import os
import getpass
import hashlib

from config import Config
from config import Colors as c
from boards import Board

def create_root(root):
    if os.path.exists(root) == False:
        try:
            os.mkdir(root, mode=0o775)
            return True
        except OSError:
            print(c.RED + "Could not create root directory. Specify another \
or create it yourself!" + c.BLACK)
            return False
    else:
        return True

root = input("Specify the root directory (e.g. /home/user/sshchan) ")
boardlist = input(
    "Specify boardlist file path (or leave blank to use default) ")
postnums = input("Specify postnums file path (or leave blank) ")
motd = input("Specify MOTD file path (or leave blank) ")
name = input("Specify server name (or leave blank) ")
# Password storage mechanism used here depends on Python
# version 3.5 or newer, hence why I'm commenting it out.
# It's not a really useful feature either, because
# admin script is separate from client script anyway.
# pt = input(
# "The current user will be set as the admin. If you wish another user to\
# be the admin, please switch users and re-run the script.\
# Type y if you want to continue.\n")
# if pt != "y":
#     sys.exit(1)
# passw = getpass.getpass("Admin password: ")
# user = getpass.getuser()

# passw = bytes(passw, "utf-8")
# # Hash the password with salt.
# salt = os.urandom(len(passw) * 2)
# sha = hashlib.sha256()
# sha.update(salt + passw)
# hash_passw = str(sha.hexdigest())

if not root:
    root = Config.defaults["rootdir"]
    if create_root(root) == False:
        sys.exit(1)
    if not boardlist:
        boardlist = Config.defaults["boardlist_path"]
    if not postnums:
        postnums = Config.defaults["postnums_path"]
    if not motd:
        motd = Config.defaults["motd_path"]
else:
    if create_root(root) == False:
        sys.exit(1)
    if not boardlist:
        boardlist = os.path.join(root, "boardlist")
    if not postnums:
        postnums = os.path.join(root, "postnums")
    if not motd:
        motd = os.path.join(root, "motd")
if not name:
    name = Config.defaults["name"]

defaults = {"rootdir": os.path.abspath(root),
            "boardlist_path": os.path.abspath(boardlist),
            "postnums_path": os.path.abspath(postnums),
            "motd_path": os.path.abspath(motd),
            "version": "0.1",
            "name": name,
            "display_legacy": "true"
            # "admin": user,
            # "salt": salt.hex(),  # This is the method that requires ver >3.5
            # "password": hash_passw
            }

# If rootdir is non-standard, create the config file in it and use that.
if root != Config.defaults["rootdir"]:
    conf_path = os.path.join(root, "sshchan.conf")
    with open(conf_path, 'w') as f:
        json.dump(defaults, f, indent=4)
    cfg = Config(conf_path)
else:
    # Or just go with default /etc/sshchan.conf.
    with open("/etc/sshchan.conf", 'w') as f:
        json.dump(defaults, f, indent=4)
    cfg = Config()

print("Creating directories and files...")
print("rootdir: {}".format(cfg.root))
print("boardlist: {}".format(cfg.boardlist_path))
print("postnums: {}".format(cfg.postnums_path))
print("motd: {}".format(cfg.motd))
print("boards: {}".format(os.path.join(cfg.root, "boards")))

try:
    os.makedirs(cfg.root)
    os.makedirs(os.path.join(cfg.root, "boards"))
except FileExistsError:
    pass
cfg.set_boardlist({})
cfg.set_postnums({})

print("Creating default board /meta/...")
meta = Board("meta", "Meta discussion", cfg)

print("All done. Run admin.py to modify and administer your textboard, or dive\
 straight in with sshchan.py!")
sys.exit(0)

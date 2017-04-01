"""
Configuration class holds settings loaded from a JSON file (or uses
defaults). Settings contain important paths that are used throughout
the program, and can be modified to contain other data easily.

Copyright (c) 2015
makos <https://github.com/makos>, chibi <http://neetco.de/chibi>
under GNU GPL v3, see LICENSE for details
"""

import os
import sys
import json
import logging

logging.basicConfig(
    filename="log",
    format="[%(lineno)d]%(asctime)s:%(levelname)s:%(message)s",
    level=logging.DEBUG)


class Colors():
    """Terminal escape codes for colored output."""

    RED = '\033[0;31m'
    YELLOW = '\033[0;33m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    BLACK = '\033[0m'

    # Bold (bright) variants of the same colors above.
    bRED = '\033[1;31m'
    bYELLOW = '\033[1;33m'
    bGREEN = '\033[1;32m'
    bBLUE = '\033[1;34m'
    bPURPLE = '\033[1;35m'
    bBLACK = '\033[1m'


class Config():
    """This class holds config data, paths to important files etc."""

    # XXX REMEMBER to put every new config option in here. XXX #
    defaults = {"rootdir": "/srv/sshchan",
                "boardlist_path": "/srv/sshchan/boardlist",
                "postnums_path": "/srv/sshchan/postnums",
                "motd_path": "/srv/sshchan/motd",
                "version": "0.1",
                "name": "sshchan",
                "prompt": "sshchan",
                "display_legacy": "False"}

    def __init__(self, cfg_path=""):
        # Find config file.

        self.path = self.look_for_config(
            cfg_path,
            os.getcwd() + "/sshchan.conf",
            os.getenv('HOME', default="~") + "/sshchan.conf",
            "/etc/sshchan.conf")

        self.root = self.get_cfg_opt("rootdir", "/srv/sshchan", fatal=True)
        self.boardlist_path = self.get_cfg_opt(
            "boardlist_path", self.root + "/boardlist")
        self.postnums_path = self.get_cfg_opt(
            "postnums_path", self.root + "/postnums")
        self.version = self.get_cfg_opt("version", "0.0")
        self.motd = self.get_cfg_opt("motd_path", "/etc/motd")
        self.server_name = self.get_cfg_opt("name", "an sshchan server")
        self.username = os.getenv("USERNAME", default="anonymous")
        self.max_boards = 10  # How many boards can be displayed in top bar.
        self.display_legacy = self.get_cfg_opt("display_legacy", "False")
        self.prompt = self.get_cfg_opt("prompt", "sshchan")
        # self.admin = settings["admin"]
        # self.salt = settings["salt"]
        # self.passwd = settings["password"]

        # Max threads on page.
        self.max_threads = 14
        # Terminal size.
        self.tty_cols = os.get_terminal_size()[0]
        self.tty_lines = os.get_terminal_size()[1]
        # Used for laprint() from Display.
        self.lines_printed = 0

    def look_for_config(self, *args):
        '''Looks for the config in the paths specified in *args until
        one that works is found.'''
        argv = list(args)
        while len(argv) != 0:
            if os.path.exists(argv[0]) == True:
                return str(argv[0])
            else:
                argv.pop(0)
                continue

        # If no config file coud be found
        print(Colors.bRED + '[FATAL] Config file could not be found.' +
              Colors.BLACK)
        sys.exit(1)

    def get_cfg_opt(self, opt_name, default, fatal=False):
        """Reads a value from the config file.
        opt_name is the key of the config value.
        default is the default value if reading fails.
        fatal, if True, means that a failure to read the option must
        terminate sshchan.
        """
        config = self.load()
        try:
            answer = config[opt_name]
            return answer
        except KeyError:
            if fatal:
                print(
                    Colors.bRED + "[FATAL] Config option \'{0}\' could \
                            not be found in file \'{1}\'.".format
                    (opt_name, self.path) + Colors.BLACK)
                sys.exit(1)
            else:
                logging.warning(
                    "Could not find the value for option {0} in config."
                    .format(opt_name))
                return default

    def set_cfg_opt(self, opt_name, new_value):
        """Set configuration option opt_name to new_value."""
        config = self.load()
        if opt_name not in self.defaults.keys():
            logging.error(
                "\"{0}\" is not a configuration option.".format(opt_name))
            return False
        config[opt_name] = new_value
        self.save(config)
        return True

    def load(self):
        """Load a JSON configuration file, or return default values."""
        try:
            with open(self.path, 'r') as c:
                config = json.load(c)
            # logging.info("Loaded JSON config file.")
            return config
        except FileNotFoundError:
            logging.warning("Config file at %s not found, returning defaults.",
                            self.path)
            return Config.defaults

    def save(self, values):
        """Save new or udpated settings to a JSON file."""
        with open(self.path, 'w') as c:
            json.dump(values, c, indent=4)
        logging.info("Dumped new settings into %s.", self.path)
        return True

    def get_boardlist(self):
        """Return the boardlist as a Python dictionary."""
        with open(self.boardlist_path, 'r') as b:
            buf = json.load(b)
        return buf

    def set_boardlist(self, values):
        """Update/create the boardlist with values.

        Boardlist is a standard Python dictionary in the form of
        {"boardname": "description", ...}
        where boardname should be just the name without any slashes
        (but they are not forbidden).
        """
        with open(self.boardlist_path, 'w') as b:
            json.dump(values, b, indent=4)
        logging.info("Updated boardlist file.")
        return True

    def get_postnums(self):
        """Return the postnums file as a Python dictionary."""
        with open(self.postnums_path, 'r') as p:
            buf = json.load(p)
        return buf

    def set_postnums(self, values):
        """Update/create the postnums for board name with value."""
        with open(self.postnums_path, 'w') as p:
            json.dump(values, p, indent=4)
        logging.info("Updated postnums file.")
        return True

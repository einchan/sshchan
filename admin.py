"""Admin commandline interface, accessible after succesful authentication.

Copyright (c) 2015
makos <https://github.com/makos/>, chibi <http://neetco.de/chibi>
under GNU GPL v2, see LICENSE for details
"""

import logging
import sys
import config
from boards import Board
from chan_mark import Marker
import helptexts

logging.basicConfig(
    filename="log",
    format="[%(lineno)d]%(asctime)s:%(levelname)s:%(message)s",
    level=logging.DEBUG)

def admin_help(c):
    print(helptexts.admin_helptext)

def cmdline(cfg, board, c):
    cmd = str(input(c.BLUE + "sshchan/" + c.RED + "ADMIN" + c.BLUE + "> "+
                    c.BLACK))
    cmd_argv = cmd.split()

    if cmd_argv[0] in ("help", "h"):
        admin_help(c)

    elif cmd_argv[0] in ("list", "ls"):
        print(board.list_boards())

    elif cmd_argv[0] == "add":
        if len(cmd_argv) > 2:
            description = ''
            board.name = cmd_argv[1]
            for word in cmd_argv[2:]:
                description += word + ' '
            board.desc = description.rstrip()
            if board.add_board():
                print(c.GREEN + "Board /", board.name, "/ added \
succesfully." + c.BLACK)
            else:
                print(c.RED + "There was an error creating the board.",
                      c.BLACK)
        else:
            print(c.RED + "Please provide board name and description \
separated by whitespace.", c.BLACK)

    elif cmd_argv[0] == "rmboard":
        if len(cmd_argv) > 1:
            board.name = cmd_argv[1]
            answer = str(input("Are you sure you want to delete \
board /" + board.name + "/? (y/n): "))
            if answer == "y":
                if board.del_board():
                    print(c.GREEN + "Board deleted succesfully.", c.BLACK)
                else:
                    print(c.RED + "Board deletion failed.", c.BLACK)
            else:
                print(c.GREEN + "No action taken.", c.BLACK)
        else:
            print(c.RED + "Please specify the board you want to delete.",
                  c.BLACK)

    elif cmd_argv[0] == "rm":
        if len(cmd_argv) >= 3:
            board.rm_post(cmd_argv[1], cmd_argv[2])
        else:
            print(c.RED + "Not enough arguments supplied." + c.BLACK)

    elif cmd_argv[0] == "rename":
        if len(cmd_argv) > 2:
            name = cmd_argv[1]
            newdesc = ' '.join(cmd_argv[2:])
            if board.rename(name, newdesc):
                print(c.GREEN + "Board renamed successfully.", c.BLACK)
            else:
                print(c.RED + "Failed to rename board.", c.BLACK)
        else:
            print(
                c.RED +
                "Please specify the board and its new description.",
                c.BLACK)

    elif cmd_argv[0] == "config":
        """Changes a configuration option."""
        if len(cmd_argv) >= 3:
            if cfg.set_cfg_opt(cmd_argv[1], " ".join(cmd_argv[2:])):
                print(
                    c.GREEN + "Configuration file changed successfully." +
                    c.BLACK)
            else:
                print(c.RED + "Failed to change configuration file.\n\
Check that the option exists first." + c.BLACK)
        else:
            print(c.RED + "Please provide at least two arguments: \
the configuration option and the value you want to change it to." + c.BLACK)

    elif cmd_argv[0] == "lsconfig":
        """List configuration options and their current values."""
        opts = sorted(cfg.defaults.keys())
        for opt in opts:
            value = cfg.get_cfg_opt(opt, c.RED + "not set /" + c.BLACK \
+ " default: " + c.GREEN + cfg.defaults[opt] + c.BLACK)
            print(opt.ljust(20) + value)

    elif cmd_argv[0] == "exit":
        sys.exit(0)

    else:
        print(c.RED + "Command " + cmd_argv[0] + " not found." + c.BLACK)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if os.path.exists(sys.argv[1]):
            cfg = config.Config(sys.argv[1])
        else:
            print("Invalid configuration file path.")
            cfg = config.Config()
    else:
        cfg = config.Config()
        marker = Marker()
        board = Board(config=cfg)
        # display = Display(config=cfg, board=board, marker=marker)
        # terminal colors object
        c = config.Colors()

    print(c.YELLOW + "sshchan-admin" + c.BLACK)
    while True:
        cmdline(cfg, board, c)

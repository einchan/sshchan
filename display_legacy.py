"""
Legacy (basic CLI) display module for sshchan.

Copyright (c) 2016
chibi <http://neetco.de/chibi>, makos <https://github.com/makos/>
under GNU GPL v2, see LICENSE for details
"""
import os
import re
import string
import subprocess
import time
from sys import exit

# Help texts and user guides
import helptexts

THREADSPERPAGE = 10 # TODO - Move to the conf file

class DisplayLegacy:

    def __init__(self, config, board, c, marker):
        # Imports
        self.board = board
        self.config = config
        self.c = c
        self.marker = marker
        # The buffer of text used by laprint() and layout()
        self.buf = ''
        # HELPTEXTS
        self.helptext = helptexts.display_legacy_helptext
        self.userguide = helptexts.display_legacy_userguide

    def display_home(self):
        self.laprint(self.c.RED + 'Welcome to ' + self.c.YELLOW + 'sshchan!\
            \n===========' + self.c.RED + '========' + self.c.BLACK)
        self.laprint(self.c.GREEN + 'SERVER:\t' + self.c.BLACK + self.config.server_name)
        self.laprint(self.c.GREEN + 'MOTD:' + self.c.BLACK)
        self.print_motd()
        # Listing boards
        self.laprint(self.c.GREEN + "BOARDS:" + self.c.BLACK)
        self.laprint(self.board.list_boards())
        self.display_connected()
        self.layout()

    def laprint(self, *args, linestart='', end='\n', markup=False, line_limit=None):
        """Add the proper text to the buffer. Its companion function is layout()."""
        
        text = " ".join(args)
        if markup == True:
            text = self.marker.demarkify(text)

        text_newline_splits = text.splitlines(keepends=True)
        text = ''
        
        if type(line_limit) == int:
            for line in text_newline_splits[:line_limit]:
                text += linestart + line
            text.rstrip("\n")
        else:
            for line in text_newline_splits:
                text += linestart + line
            
        self.buf += text
        self.buf += end

    def layout(self):
        """Print out a page's worth of text in the buffer."""
        lines = 0
        chars = 0
 
        for c in self.buf:
            # Stops decoding errors
            c = c.encode("utf-8", "replace").decode("utf-8")
            if c in string.printable:
                chars += 1
            if c == '\n':
                chars = 0
                lines += 1
            if chars == self.config.tty_cols:
                chars = 0
                lines += 1
            print(c, end='')
            self.buf = self.buf[1:]
#            if lines == self.config.tty_lines - 2:
#                print(self.c.GREEN + "Page too long to display.", \
#                   "Type 'page' and hit Enter to see the rest." + self.c.BLUE)
#                lines += 1
#                break

        if lines <= self.config.tty_lines:
            lines_to_print = self.config.tty_lines - (lines + 1)
            print('\n' * lines_to_print, end='')

    def print_motd(self):
        """Prints the MOTD."""
        try:
            m = open(self.config.motd)
            motdbuf = m.read()
            m.close()
            self.laprint(motdbuf)     
        except FileNotFoundError:
            self.laprint("\'Shitposting was never the same\' --satisfied sshchan user")

    def display_connected(self):
        """Prints out the number of people currently connected to the ssh port."""
        try:
            connected = subprocess.check_output("netstat -atn | grep ':22' | grep 'ESTABLISHED' | wc -l", shell=True)
            connected = int(connected)
            self.laprint(self.c.YELLOW + "Connected: " + self.c.BLACK + str(connected))
        except:
            self.laprint(self.c.YELLOW + "Connected: " + self.c.BLACK + "It is a mystery")

    def display_help(self, cmd=None):
        """Display either the entire help message or just the help
        for a particular command (cmd)"""
        if cmd == None:
            for key in sorted(self.helptext.keys()):
                print(self.c.GREEN + self.helptext[key][0] + self.c.YELLOW, \
                    self.helptext[key][1] + "\n" + self.c.BLACK + self.helptext[key][2])
            print(helptexts.markup_helptext)
        else:
            try:
                print(self.c.GREEN + self.helptext[cmd][0] + self.c.YELLOW, \
                    self.helptext[cmd][1] + "\n" + self.c.BLACK + self.helptext[cmd][2])
            except KeyError:
                print(self.c.RED + "Help for that command could not be found." + self.c.BLACK)

    def convert_time(self, stamp):
        """Convert UNIX timestamp to regular date format.

        @stamp - integer representing UNIX timestamp."""
        return str(time.strftime(
            '%H:%M:%S %d %b %Y',
            time.localtime(int(stamp))))

    def trip_convert(self, name):
        """Scans a name for a tripcode and converts it if so."""
        trip = re.split("##(?P<code>.*)", name)
        if (len(trip) > 1):
            #import zlib
            #name_proper = trip[0]
            #tripcode = zlib.crc32(trip[1])
            #digest = repr(tripcode) 
            #return name_proper + " !" + digest
            return name
        else:
            return name

    def display_board(self, page=1):
        """Displays the OPs of the threads on a board."""
        if self.board.name == '':
            print(self.c.RED + "You are not on a board." + self.c.BLACK)
            self.display_help(cmd="cd")
            return False

        # Checks if the path to the board's index file exists.
        # If it does not, the board most likely does not exist.
        if self.board.board_exists(self.board.name) == False:
            return False

        index = self.board.get_index()
        
        if type(THREADSPERPAGE) == int:
            first_thread_to_display = (THREADSPERPAGE * page) - THREADSPERPAGE
            last_thread_to_display = (THREADSPERPAGE * page)
            if last_thread_to_display > len(index):
                last_thread_to_display = len(index)
                first_thread_to_display = len(index) - THREADSPERPAGE
                if len(index) < THREADSPERPAGE:
                    first_thread_to_display = 0
        else:
            first_thread_to_display = 0
            last_thread_to_display = len(index)
        
        
        for x in reversed(range(first_thread_to_display, last_thread_to_display)): # reversed() makes newest threads appear at the bottom.
            thread = index[x]
            thread_id = thread[0]
            del thread
            self.display_thread(thread_id, index=index, op_only=True)
        self.layout()

    def display_thread(self, thread_id, index=None, op_only=False, replies=1000):
        """Displays a thread.
        thread_id is self-explanatory.
        index: the thread index. It is an argument to cut down on reading
         the index file for every thread.
        op_only: if True, print only the OP post.
        replies is the number of replies to print."""
        if index == None:
            index = self.board.get_index()

        post_line_limit = None
        # The index of the thread in the index file
        thread_pos = self.board.thread_exists(int(thread_id))

        if thread_pos == -1: # -1 is the false return value for thread_exists()
            print(self.c.RED + 'Thread not found.' + self.c.BLACK)
            return False
        else:
            thread = index[thread_pos]

        if op_only == True:
            replies = 3 
            post_line_limit = 5

        for x in range(2, replies): # reversed() makes the newest posts appear at the bottom
            try:
                reply = thread[x]
            except IndexError:
                break

            if len(reply) == 3: # The old json format - just date, post_no and post_text
                name = "Anonymous"
                date = self.convert_time(int(reply[0]))
                post_no = str(reply[1])
                post_text = str(reply[2]).rstrip()
            else:
                name = reply[0] 
                date = self.convert_time(int(reply[1]))
                post_no = str(reply[2])
                post_text = str(reply[3]).rstrip()

            # If it is not the OP post, prepend two spaces to every line.
            # Makes it look better. 
            if x == 2:
                lst = ''
            else:
                lst = '  '

            self.laprint(self.c.YELLOW + name, end=' ', linestart=lst)
            self.laprint(self.c.GREEN + date + self.c.BLACK + ' No.' + post_no, end=' ')
            # If it is the OP post, print the subject
            if x == 2:
                self.laprint(self.c.RED + str(thread[1]) + self.c.BLACK)
            else:
                self.laprint()
            self.laprint(post_text, markup=True, line_limit=post_line_limit, linestart=lst)

        if op_only == True:
            self.laprint(self.c.GREEN + str(len(thread) - 3), "replies \
hidden. Type \'v " + str(thread_id) + "\' to view them.\n")

        return True

    def post_menu(self, thread_id=-1):
        """Get post from the user and send it to addPost()."""
        # Get name. Default is the username of the controlling user of
        # the sshchan process.
        name = str(input("Name: [default: " + self.c.YELLOW + \
self.config.username + self.c.BLACK + "] "))
        if name == '':
            name = self.config.username
        else:
            name = self.trip_convert(name)

        # Get the post text.
        print("Post text:\n" + self.c.GREEN + \
"[Hint: leave a blank line to complete the post.]" + self.c.BLACK)
        post_text = ''
        blanks = 0 # How many blank lines have been entered

        while True:
            line = input()
            if line == '':
                blanks += 1
            else:
                blanks = 0
            if blanks == 2:
                break 
            post_text += line + "\n"

        # If the user did not post anything, show an error.
        if post_text == '\n':
            print(self.c.RED + "You have made an empty post. Scrapping..." \
+ self.c.BLACK)
            return False

        post_text = post_text.rstrip()

        if thread_id == -1: # If a new thread is to be posted
            subject = str(input("Subject: "))
        else:
            subject = ""

        name = self.marker.esc(name)
        subject = self.marker.esc(subject)
        post_text = self.marker.esc(post_text)

        success = self.board.add_post(post_text, name=name, \
                  subject=subject, thread_id=thread_id)
        if success == True:
            print(self.c.GREEN + "Post successful!" + self.c.BLACK)
        else:
            print(self.c.RED + "Post failed." + self.c.BLACK)

"""
Board class allows operation on a board, like posting, creating threads etc.
If it is instantiated with name parameter that isn't found in boardlist
file, the board and relevant files (index, postnums) are automatically created
and updated.

Copyright (c) 2015
makos <https://github.com/makos>, chibi <http://neetco.de/chibi>
under GNU GPL v2, see LICENSE for details
"""

import json
import os
import logging
import shutil
import time
import re

from config import Colors

logging.basicConfig(
    filename="log",
    format="[%(lineno)d]%(asctime)s:%(levelname)s:%(message)s",
    level=logging.DEBUG)


class Board():
    """Class holding data of the currently selected board."""

    def __init__(self, name='', desc='', config=None):
        assert config is not None, logging.critical(
            "Board.__init__: config is None")
        # Configuration object used to read / write config values.
        self.config = config
        self.c = Colors()

        self._name = name.lower()
        self._desc = desc
        self.thread = 0 # The thread that the user is viewing.
        self.path = os.path.join(self.config.root, "boards", self._name)
        self.index_path = os.path.join(self.path, "index")
        self.boardlist_path = self.config.boardlist_path

        if self.add_board():
            logging.info(
                'Board "/%s/ - %s" added succesfully.', self._name, self._desc)

    def __eq__(self, other):
        """Equality (==) operator overload method."""
        if self._name == other.name and self._desc == other.desc:
            return True
        else:
            return False

    def list_boards(self):
        boardlist = self.config.get_boardlist()
        postnums = self.config.get_postnums()
        print(postnums)
        list_string = ''
        for board in sorted(boardlist):
            desc = boardlist[board]
            postnum = postnums[board]
            list_string += "/{0}/".format(board).ljust(12) + \
                "{0}".format(desc) + "{0} posts\n".format(postnum).rjust(12)
        return list_string

    def add_board(self):
        """Adds board to the boardlist and creates all relevant files.

        If the Board class is instantiated with a name parameter that
        isn't present in the current boardlist, the board is
        automatically added and all directories and files are also
        created.
        """

        if self._name in self.config.get_boardlist().keys() \
                or self._name == '':
            return False
        # Add the board to boardlist.
        buf = self.config.get_boardlist()
        buf[self._name] = self._desc
        self.config.set_boardlist(buf)
        # Create the board directory.
        try:
            os.makedirs(self.path)
        except OSError as e:
            logging.error("Board.addBoard(): %s", e)
        # Create the index file.
        self.set_index([])
        # Edit postnums.
        postn = self.config.get_postnums()
        postn[self._name] = 0
        self.config.set_postnums(postn)

        return True

    def del_board(self):
        if self._name != "":
            if os.path.exists(self.index_path) == False:
                return False
            os.remove(self.index_path)
            os.rmdir(self.path)
            # Boardlist
            boardlist = self.config.get_boardlist()
            del boardlist[self._name]
            self.config.set_boardlist(boardlist)
            # Postnums
            postn = self.config.get_postnums()
            del postn[self._name]
            self.config.set_postnums(postn)
            logging.info("Board %s deleted succesfully.", self._name)
            self._name = ""
            self.desc = ""
            self.path = ""
            self.index_path = ""
            return True
        else:
            return False

    def get_index_sort_key(self, item):
        """The key function when sorting the index file.
        Returns the timestamp of the last post in the thread (item)."""
        if len(item[-1]) == 4:
            return item[-1][1]
        else:
            return item[-1][0]

    def get_index(self):
        """Returns a list containing the board's index."""
        with open(self.index_path, 'r') as i:
            buf = json.load(i)
            buf.sort(key=self.get_index_sort_key, reverse=True)
        return buf

    def set_index(self, values):
        """Update the board's index with new values."""
        with open(self.index_path, 'w') as i:
            json.dump(values, i, indent=4)
        return True

    @property
    def name(self):
        """Getter for name field."""
        return self._name

    @name.setter
    def name(self, value):
        """Setter for name field.

        Assignments like board.name = 'b' should ONLY be used
        if the board already exists.
        If you want to create a board,
        use the addBoard() method."""
        self._name = value
        self.path = os.path.join(self.config.root, "boards", self._name)
        self.index_path = os.path.join(self.path, "index")
        self.boardlist_path = self.config.boardlist_path

    @property
    def desc(self):
        """Getter for description field."""
        return self._desc

    @desc.setter
    def desc(self, value):
        """Setter for description field."""
        self._desc = value

    def rename(self, board_name, desc):
        """Changes the description of board to desc."""
        buf = self.config.get_boardlist()
        board_name = self.convert_board_name(board_name)

        if board_name in buf.keys():
            # Change boardlist.
            buf[board_name] = desc
            self.config.set_boardlist(buf)
            return True

    def convert_board_name(self, board):
        """Removes the slashes from a user-inputted board name."""
        board = re.sub("/(?P<boardn>.*?)/", "\g<boardn>", board)
        return board

    def convert_post_id(self, post_id):
        try:
           post_id = abs(int(post_id))
           return post_id
        except ValueError:
           print(self.c.RED + "\'" + post_id + "\' is not a thread \
number." + self.c.BLACK)
           return False

    def collect_post_ids(self, thread):
        '''Returns all the post_ids within the thread group 'thread'''
        thread_post_ids = []
        for y in range(2, len(thread)):
            if len(thread[y]) == 3:
                thread_post_ids.append(thread[y][1])
            elif len(thread[y]) == 4:
                thread_post_ids.append(thread[y][2])
        return thread_post_ids

    def board_exists(self, board):
        board = self.convert_board_name(board)
        _index_path = os.path.join(self.config.root, "boards", board, "index")
        if not os.path.exists(_index_path):
            print(self.c.RED + 'Board /' + self.name + '/ does not exist.' + self.c.BLACK)
            self.name = '' 
            self.thread = 0
            return False
        else:
            self.name = board
            return True

    def thread_exists(self, post_id, return_id=False):
        '''Checks which thread to reply to.
        First, it checks the thread_ids. If there is a match, it returns it.
        If not, then the user is trying to reply to a post within a thread.
        It finds the thread in which the post can be found, and returns that
        thread's index. If it can't be found, it fails.
        If return_id is true, the thread id is returned instead of the index.'''
        post_id = self.convert_post_id(post_id)
        if post_id == False:
            return -1

        index_page = self.get_index()
        for x in range(0, len(index_page)):
            thread = index_page[x]
            if post_id == thread[0]: # If the post_id is the thread_id
                if return_id:
                    return thread[0]
                else:
                    return index_page.index(thread)
            else:
                thread_post_ids = self.collect_post_ids(thread)
                if post_id in thread_post_ids:
                    if return_id:
                        return thread[0]
                    else:
                        return index_page.index(thread)
        return -1 

    def add_post(self, post_text, name="Anonymous", subject="", thread_id=-1):
        """Posts a thread or a reply to a thread.

        If thread_id is not specified (i.e. = -1), a new thread
        is created. Posting depends on the file (rootdir)/postnums
        which has the following JSON structure:
        [{'a': max_post_no}, {'b': max_post_no}, ...]
        where max_post_no is the current highest post number.

        Thread / post format is as follows:
        index page is a standard Python list, where
        index[0] is the first thread with ID 1,
            index[1] is the second thread etc.
        index[n][0] is the ID of n-th thread
        index[n][1] is the subject
        index[n][2] is the first reply, where
            index[n][2][0] is the name (default is Anonymous)
            index[n][2][1] is the Unix timestamp
            index[n][2][2] is the ID (post number)
            index[n][2][3] is the text (body)
        index[n][k], where k > 1, is the k-th reply to n-th thread
        """
        index_page = self.get_index()
        success = False

        postnums = self.config.get_postnums()
        max_post_no = postnums[self._name]
        timestamp = int(time.time())

        if thread_id == -1:
            # Add a new thread.
            index_page.append(
                [max_post_no + 1, subject,
                 [name, timestamp, max_post_no + 1, post_text]])
            self.set_index(index_page)
            postnums[self._name] += 1
            self.config.set_postnums(postnums)
            success = True
        else:
            # Add reply to an existing thread.
            thread_id = abs(thread_id)
            # Maybe get a better search algorithm?
            for x in range(0, len(index_page)):
                thread = index_page[x]
                cur_thread_id = thread[0]

                if cur_thread_id == thread_id:
                    thread.append([name, timestamp, max_post_no + 1, post_text])
                    self.set_index(index_page)
                    postnums[self._name] += 1
                    self.config.set_postnums(postnums)
                    success = True

        return success

    def rm_post(self, board, post_id):
        """Removes the post with post_id on board."""
        if self.board_exists(board) == False:
            return False

        post_id = self.convert_post_id(post_id)
        if post_id == False:
            return False

        index = self.get_index()
        thread_index = self.thread_exists(post_id)
        if thread_index == -1:
            print(self.c.RED + "Could not find post." + self.c.BLACK)
            return False
        else:
            thread = index[thread_index]

        for x in range(2, len(thread)):
            post = thread[x]
            if len(post) == 3: # Old json strucutre
                this_post_id = post[1]
                post_text = post[2]
            elif len(post) == 4: # New json strucutre
                this_post_id = post[2]
                post_text = post[3]

            if this_post_id == post_id:
                print(self.c.YELLOW + "Deleting post:\n" + self.c.BLACK + \
                "Post no.: " + str(this_post_id) + "\n" + \
                "Post content:\n" + post_text[:500] + "\n")
                answer = str(input(self.c.GREEN + "y" + self.c.BLACK + "/" + \
                         self.c.RED + "n" + self.c.BLACK + "? "))

                if answer != "y":
                    print(self.c.YELLOW + "Deletion aborted." + self.c.BLACK)
                    return False 

                if x == 2: # If it is the OP post, delete the entire thread
                    del index[thread_index]
                else:
                    del index[thread_index][x]

                self.set_index(index)
                print(self.c.GREEN + "Post removed successfully." + self.c.BLACK)
                break

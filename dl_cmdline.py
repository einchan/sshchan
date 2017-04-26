class DisplayLegacyCmdline:
    """
    This class defines how the CLI operates.
    The run() function is called when sshchan starts.
    Many of the actual functions which do the work live in
    display_legacy.py's DisplayLegacy class, which is imported
    here as 'dl'.
    """
    def __init__(self, board, c, config, dl, marker):
        self.board = board
        self.c = c # Colours
        self.config = config
        self.dl = dl # DisplayLegacy functions
        self.marker = marker

    def run(self):
        self.dl.display_home()
        while True:
            self.cmdline()

    def cmdline_board(self, board=0, page=1):
        # NOTE: The buffer needs to be cleared before almost every
        # command that uses layout() so that stuff from a previous
        # command does not get left behind in the buffer and printed
        self.dl.buf = '' # Renew buffer
        if type(board) == int:
            self.board.name = ''
            self.board.thread = 0
            self.dl.display_home()
        else:
            self.board.name = self.board.convert_board_name(board)
            self.board.thread = 0
            self.dl.display_board(page)


    def cmdline_reply(self, cmd_argv):
        """The spaghetti code for the 're' command."""
        if self.board.name == '':
            # sshchan///> re /board/ 
            if len(cmd_argv) == 2:
                if self.board.board_exists(\
                   self.board.convert_board_name(cmd_argv[1])) == False:
                    return False
                self.cmdline_reply(["re"])
            else:
                print(self.c.RED + "Too few or too many arguments provided."\
                    + self.c.BLACK)
                self.dl.display_help(cmd="re")
                return False

        else:
            if len(cmd_argv) == 1:
                if self.board.thread == 0:
                # sshchan/board//> re
                    self.dl.post_menu()
                else:
                # sshchan/board/1/> re
                    self.dl.post_menu(thread_id=self.board.thread_exists(\
                    self.board.thread, return_id = True))

            # sshchan/board//> re 1
            elif len(cmd_argv) >= 2:
                thread_id = self.board.thread_exists(cmd_argv[1], return_id=True)
                if thread_id == -1:
                    return False
                else:
                    self.board.thread = thread_id
                    self.dl.post_menu(thread_id=thread_id)

    def cmdline_view(self, cmd_argv):
        self.dl.buf = '' # Renew buffer
        if len(cmd_argv) == 1:
            self.board.thread = 0
            return True
        if self.board.name == '':
            print(self.c.RED + "You are not on a board. Use \'cd\' to change boards."\
            + self.c.BLACK)
            return False

        try:
            success = self.dl.display_thread(cmd_argv[1])
            if success == True:
                self.board.thread = self.board.thread_exists(cmd_argv[1], return_id=True)
                self.dl.layout()

        except ValueError:
            print(self.c.RED + cmd_argv[1], "is not a thread or post number.")
            self.dl.display_help(cmd="view")

    def cmdline(self):
        """The command line that controls sshchan's behaviour."""
        # Printing out prompt
        if self.board.thread == 0:
            prompt_thread = ''
        else:
            prompt_thread = str(self.board.thread)
        print(self.c.BLUE + self.config.prompt + "/" + self.board.name + "/" +\
            self.c.PURPLE + prompt_thread + self.c.BLUE + "/>" + self.c.BLACK, end=' ')

        cmd = str(input())
        cmd = self.marker.esc(cmd)
        cmd_argv = cmd.split()

        if len(cmd_argv) == 0:
            return False

        if cmd_argv[0] in ("exit", "quit", "q"):
            exit(0)

        elif cmd_argv[0] in ("h", "help"):
            if len(cmd_argv) == 2:
                #if cmd_argv[1] == "user":
                    #self.dl.laprint(self.userguide) # This is broken i don't know why it's here. There's no such thing as self.userguide, and what is a user anyway?
                    #self.dl.layout()
                #else:
                self.dl.display_help(cmd=str(cmd_argv[1]))
            else:
                self.dl.display_help()
                print("\nType \'help user\' for a guide to sshchan.")

        elif cmd_argv[0] in ("b", "board", "cd"):
            if len(cmd_argv) > 1:
                self.cmdline_board(board=cmd_argv[1])
            else:
                self.cmdline_board()

        elif cmd_argv[0] in ("ls", "list"):
            self.dl.buf = ''
            self.dl.laprint(self.c.GREEN + "BOARDS:" + self.c.BLACK)
            self.dl.laprint(self.board.list_boards())
            self.dl.layout()

        elif cmd_argv[0] in ("page", "p"):
            if self.board.name == "":
                print(self.c.RED + "You are not on a board yet. Use \'cd\' to change boards." + self.c.BLACK)
                self.dl.display_help()
            elif len(cmd_argv) < 2:
                print(self.c.RED + "You must give the number of the page you wish to view!" + self.c.BLACK)
                self.dl.display_help()
            else:
                try:
                    self.cmdline_board(board=self.board.name, page=int(cmd_argv[1]))
                except ValueError:
                    print(self.c.RED + cmd_argv[1], "is not a number.")
                    self.dl.display_help(cmd="page")
                    

        elif cmd_argv[0] in ("re", "reply"):
            self.cmdline_reply(cmd_argv)

        elif cmd_argv[0] in ("refresh", "rb"):
            self.dl.display_board()
            self.board.thread = 0

        elif cmd_argv[0] == "rt":
            if self.board.name != '' and self.board.thread != 0:
                self.dl.display_thread(self.board.thread)
                self.dl.layout()

        elif cmd_argv[0] in ("v", "view"):
            self.cmdline_view(cmd_argv)

        else:
            print(self.c.RED + "Command \'" + cmd_argv[0] + "\' not found." + self.c.BLACK)
            self.dl.display_help()


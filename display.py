# -*- coding: utf-8 -*-
"""
ncurses GUI (TUI?) made possible thanks to urwid framework.

http://urwid.org/
Unfortunately urwid, even though it's way better than raw Python curses, has
very little documentation, and recognition among programmers. Most problems
I've encountered had to be solved alone. Manual and reference are kinda useful,
but the tutorial is completely useless. That's why I tried to document and
comment this code as much as I could, to share what I have learned myself
in the past few days.

Copyright (c) 2015
makos <https://github.com/makos>, chibi <http://neetco.de/chibi>
under GNU GPL v2, see LICENSE for details
"""

import logging
import time
import urwid as ur


logging.basicConfig(
    filename="log",
    format="[%(lineno)d]%(asctime)s:%(levelname)s:%(message)s",
    level=logging.DEBUG)


class CleanButton(ur.Button):
    """Custom button class, without additional decorators around it."""
    # TODO: make the text inside those buttons CENTERED.
    # It's way harder than it sounds.

    def __init__(self, caption, callback, data):
        super(CleanButton, self).__init__(caption, callback, data)
        self._w = ur.SelectableIcon(caption, 0)


class MyOverlay(ur.Overlay):

    def __init__(
            self, top_w, bottom_w,
            align, width, valign, height,
            min_width=None, min_height=None,
            left=0, right=0,
            top=0, bottom=0, parent=None):
        super(MyOverlay, self).__init__(
            top_w, bottom_w,
            align, width, valign, height,
            min_width, min_height,
            left, right,
            top, bottom)
        self.parent = parent

    def keypress(self, size, key):
        super(MyOverlay, self).keypress(size, key)
        if key == "tab":
            pass
        elif key == "esc":
            self.parent.button_press(None, "back")
        return True


class Loop(ur.MainLoop):
    """Controller class for MainLoop instance of the program."""

    palette = [
        (None, "light gray", "black"),
        ("bg", "", "black"),
        ("yellow", "yellow", "black"),
        ("red", "dark red", "black"),
        ("b_red", "light red", "black"),
        ("reverse_red", "dark red,standout", "black"),
        ("green", "dark green", "black"),
        ("b_green", "light green", "black"),
        ("reverse_green", "dark green,standout", "black"),
        ("cyan", "dark cyan", "black"),
        ("b_cyan", "light cyan", "black"),
        ("blue", "dark blue", "black"),
        ("b_blue", "light blue", "black"),
        ("underline", "underline", "black"),
        ("bold", "light gray,bold", "black"),
        ("reverse", "light gray,standout", "black")
    ]

    def __init__(self, top_widget, input_handler):
        """Initialize parent class, get terminal size and set up stack.

        The stack holds all widgets that were displayed in order that
        they've appeared. This way going "back" is easily achieved
        just by popping the stack and setting `widget` property to point
        at the current topmost widget.

        Note: it should not be used directly, just use the setters and
        deleters below.
        """
        super(Loop, self).__init__(
            top_widget,
            self.palette,
            unhandled_input=input_handler)
        self.dimensions = self.screen.get_cols_rows()
        self._widget_stack = []

    # Properties to ease manipulation of top-level widgets.
    @property
    def baseWidget(self):
        """Read-only property returns the very lowest widget."""
        return self.widget.base_widget

    @property
    def origWidget(self):
        """Return widget one lower than the topmost one."""
        return self.widget.original_widget

    @property
    def Widget(self):
        """Returns the full topmost widget, with all wrappers etc."""
        return self.widget

    @Widget.setter
    def Widget(self, widget):
        """Setter for topmost widget, used to switch view modes.

        @widget - widget instance, most probably ur.Frame

        Assigns a new topmost widget to be displayed, essentially
        allowing us to switch between modes, like board view,
        main menu, etc.
        """
        self._widget_stack.append(widget)
        self.widget = widget

    @Widget.deleter
    def Widget(self):
        """Delete the topmost widget and draw new topmost one.

        Usage:
            `del self.loop.Widget` will remove current widget from view and
                draw the earlier one.
        """
        self._widget_stack.pop()
        self.widget = self._widget_stack[-1]

    @property
    def stack_len(self):
        return len(self._widget_stack)

    @property
    def frameBody(self):
        """Returns body (a list of widgets in the form of
        Simple[Focus]ListWalker) of top-level Frame widget to manipulate."""
        return self.widget.original_widget.contents["body"][0]. \
            original_widget.body


class Display:

    def __init__(self, config, board):
        """Initialize the most needed components."""
        self.config = config
        self.board = board

        self.header = None
        self.footer = None
        # Some sugar.
        self.div = ur.Divider()
        # Used in list_boards().
        self.boards_count = 0

        self.loop = Loop(None, self.unhandled)
        # Calculate min_width and left/right margins for Padding widgets.
        self.width = self.loop.dimensions[0] // 2
        self.margin = int((self.loop.dimensions[0] - self.width) * 0.60)
        # Flag for checking if board list is currently being displayed.
        self.list_visible = False
        # This flag needs to be here to fix a bug where Enter doesn't work
        # after hitting 'h' twice.
        self.help_flag = False
        # Another flag, this one is for board list display - it should only
        # be printed in the main menu/MOTD screen, nowhere else.
        self.motd_flag = False

    def run(self):
        """This method needs to be called to actually start the display.

        To switch to another view (another Frame widget), use the
        `@widget.setter` property of Loop. To return to earlier view
        (or close a pop-up), use `@widget.deleter`. To interact with the
        body of current Frame, use `@frameBody` property.
        """
        frame = self.MOTD_screen()
        # Top-level widget finished initializing, so let's assign it.
        self.loop.Widget = ur.AttrMap(frame, "bg", None)
        self.loop.run()

    def MOTD_screen(self):
        """MOTD display method - first screen shown."""
        self.motd_flag = True
        self.header = self.make_header()

        mid = ur.Padding(ur.ListBox(
            ur.SimpleFocusListWalker([
                self.div, ur.Text([("red", "Welcome to "),
                                   ("yellow", "sshchan!\n==========="),
                                   ("red", "========\n"),
                                   ("green", "SERVER: "),
                                   self.config.server_name,
                                   ("green", "\nMOTD:\n")], "center"),
                self.div])), "center", ("relative", 60), self.width,
            self.margin, self.margin)

        # TODO: add currently online users to the footer.
        self.footer = ur.AttrMap(ur.Text(
            " " + self.config.server_name + " " + self.config.version +
            " | Press H for help", align="center"), "reverse", None)

        try:
            with open(self.config.motd, 'r') as m:
                buf = m.read()
        except FileNotFoundError:
            buf = "---sshchan! woo!---"
        motd = ur.Text(buf, "center")
        mid.original_widget.body.append(motd)
        mid.original_widget.body.append(self.div)

        return ur.Frame(mid, self.header, self.footer, focus_part="body")

    def make_header(self):
        """Populate the row of board buttons on top."""
        # TODO: make it intelligent so it fits in the terminal window
        # and doesn't depend on arbitrary values from config.
        # Keep count of number of printed boards so we won't print too many.
        i = 0
        longest = 0
        btn_list = []

        for board in sorted(self.config.get_boardlist().keys()):
            # This `if` block should be removed when the function learns to
            # calculate horizontal space required.
            if i >= self.config.max_boards:
                break
            if len(board) > longest:
                longest = len(board)
            btn_list.append(CleanButton(
                "/" + board + "/", self.button_press, board))
            i += 1

        # `longest + 2` to account for slashes.
        return ur.AttrMap(ur.GridFlow(btn_list, longest + 2, 1, 0, "center"),
                          "reverse")

    def button_press(self, button, data):
        """Generic callback method for buttons (not key-presses!).

        @button - button object instance that called the method,
        @data - (string) additional data provided by calling button
            instance, used to define what action should be taken.
        """
        if data in self.config.get_boardlist().keys():
            # Board button was pressed.
            # If the board was entered from any view other than MOTD
            # (e.g. other board view), pop the widget from stack, so
            # pressing ESC will return to MOTD.
            if not self.motd_flag:
                del self.loop.Widget
            self.motd_flag = False
            self.help_flag = False
            self.board.name = data
            # Transfer control to BoardView instance.
            BoardView(self.loop, self.config, self.board, self)
        elif data == "back":
            # Clear the help flag, to avoid bugs.
            self.help_flag = False
            # Go back, restore saved widgets from previous screen.
            del self.loop.Widget
            # Check if we're on the main screen to avoid bugs.
            if self.loop.stack_len == 1:
                self.motd_flag = True
        elif data == "quit":
            # Bai
            raise ur.ExitMainLoop()

    def unhandled(self, key):
        """Input not handled by any other widgets.

        @key - string representing key that was pressed.

        Most key presses inside sshchan should be handled by this function.
        Buttons don't need handling here, they respond to Enter, Space or
        mouse clicks.
        """
        # Refresh screen dimensions in case terminal is resized.
        self.loop.dimensions = self.loop.screen.get_cols_rows()
        # Calculate width and margins of Padding based on terminal size.
        self.width = self.loop.dimensions[0] // 2
        self.margin = int((self.loop.dimensions[0] - self.width) * 0.60)

        if key in ("Q", "q"):
            self.quit_prompt()
        elif key == "tab":
            # Switch focus from body to top bar and vice versa.
            if self.loop.baseWidget.focus_position == "header":
                self.loop.baseWidget.focus_position = "body"
            else:
                self.loop.baseWidget.focus_position = "header"
        elif key in ("H", "h"):
            # Disable MOTD flag.
            self.motd_flag = False
            if not self.help_flag:
                self.loop.Widget = self.show_help()
        elif key in ("B", "b"):
            if not self.list_visible and self.motd_flag:
                # If board list isn't currently being displayed, let's show it.
                self.list_visible = True
                self.loop.frameBody.extend(self.list_boards())
            elif self.list_visible and self.motd_flag:
                # Board list was being displayed, get rid of it.
                for i in range(self.boards_count):
                    self.loop.frameBody.pop()
                self.list_visible = False
        elif key == "esc":
            # If not on the main screen, ESC goes back, otherwise try to quit.
            if not self.motd_flag:
                self.button_press(None, "back")
            else:
                self.quit_prompt()

        # Urwid expects the handler function to return True after it's done.
        return True

    def quit_prompt(self):
        """Pop-up window that appears when you try to quit."""
        # Nothing fancy here.
        question = ur.Text(("bold", "Really quit?"), "center")
        yes_btn = ur.AttrMap(ur.Button(
            "Yes", self.button_press, "quit"), "red", None)
        no_btn = ur.AttrMap(ur.Button(
            "No", self.button_press, "back"), "green", None)

        prompt = ur.LineBox(ur.ListBox(ur.SimpleFocusListWalker(
            [question, self.div, self.div, no_btn, yes_btn])))

        # The only interesting thing in this method is this Overlay widget.
        overlay = MyOverlay(
            prompt, self.loop.baseWidget,
            "center", 20, "middle", 8,
            16, 8,
            parent=self)
        self.loop.Widget = overlay

    def show_help(self):
        """Create and return Frame object containing help docs."""
        # Flags are gr8 against bugs.
        self.help_flag = True

        help_header = ur.Text(("green", "SSHCHAN HELP"), "center")
        pg1 = ur.Text(
            [("bold", "sshchan "), "is a textboard environment designed \
to run on remote SSH servers with multiple anonymous users simultaneously \
browsing and posting."], "center")
        pg2 = ur.Text(("bold", "Keybindings:"))
        pg3 = ur.Text([("green", "TAB"),
                       (
                           None,
                           " - switch focus between main body and top bar")])
        pg4 = ur.Text(
            [("green", "H h"), (None, " - display this help dialog")])
        pg5 = ur.Text(
            [("green", "B b"), (None, " - view available boards")])
        pg6 = ur.Text(
            [("green", "ESC"),
             (
                 None,
                 " - go back one screen (exits on MOTD screen)")])

        back_btn = ur.AttrMap(
            ur.Button("Back", self.button_press, "back"), "red", "reverse")

        help_body = ur.Padding(ur.ListBox(ur.SimpleListWalker([
            self.div, help_header, self.div, pg1, self.div, pg2,
            pg3, pg4, pg5, pg6, self.div, back_btn])),
            "center", self.width, 0, self.margin, self.margin)

        return ur.AttrMap(ur.Frame(help_body, self.header, self.footer,
                                   "body"), "bg")

    def list_boards(self):
        """Display a column of buttons listing all available boards."""
        boards = self.config.get_boardlist()

        btn_list = []
        for board, desc in sorted(boards.items()):
            btn_list.append(ur.AttrMap(ur.Button(
                "/" + board + "/   -   " + desc, self.button_press, board),
                None, "reverse"))
            btn_list.append(self.div)

        # boards_count is here so the list can be dynamically displayed.
        self.boards_count = len(btn_list)
        return btn_list


class BoardView:

    def __init__(self, loop, config, board, parent):
        self.loop = loop
        self.config = config
        self.board = board
        self.parent = parent

        # Move this out to Loop or Display, so it's not reset
        # every time the user switches boards
        self.name = "Anonymous"

        self.show_board()

    def convert_time(self, stamp):
        """Convert UNIX timestamp to regular date format.

        @stamp - integer representing UNIX timestamp."""
        return str(time.strftime(
            '%H:%M:%S %d %b %Y',
            time.localtime(int(stamp))))

    def parse_post(self, post):
        """Read post JSON and return values in easily-readable dictionary."""
        # Old json - without name field
        if len(post) == 3:
            parsed_post = {
                "name": "Anonymous",
                "stamp": self.convert_time(post[0]),
                "id": str(post[1]),
                "text": ur.Text(post[2])
            }
        else:
            parsed_post = {
                "name": post[0],
                "stamp": self.convert_time(post[1]),
                "id": str(post[2]),
                "text": ur.Text(post[3])
            }

        return parsed_post

    def show_board(self):
        index = self.board.get_index()
        new_btn = ur.AttrMap(
            ur.Button("New thread", self.reply_box, -1), "green", "b_green")
        thread_list = ur.SimpleFocusListWalker(
            [ur.Padding(new_btn, "center", ("relative", 40)), self.parent.div])

        for thread in index:
            # Check subject, because empty subject with set color attribute
            # produces wrong output.
            subject = ("reverse_red", thread[1])
            if subject[1] == "":
                subject = (None, "")

            op = self.parse_post(thread[2])

            post_info = ur.Text([("reverse_green", op["name"]),
                                 " " + op["stamp"] + " ", subject, " No. " +
                                 op["id"]])
            reply_btn = ur.AttrMap(CleanButton(
                "Reply", self.print_thread, op["id"]), None, "reverse")

            replies = []
            if len(thread) > 3:
                for i in range(3, 6):
                    try:
                        reply = self.parse_post(thread[i])
                        replies_info = ur.Text(
                            [("green", reply["name"]), " " + reply["stamp"]])
                        no_btn = CleanButton(
                            "No. " + reply["id"],
                            self.print_thread,
                            reply["id"])

                        replies_header = ur.Padding(ur.Columns(
                            [("pack", replies_info), ("pack", no_btn)],
                            1), left=1)
                        reply_text = ur.Padding(reply["text"], left=1)

                        replies.extend(
                            [replies_header, reply_text, self.parent.div])
                    except IndexError:
                        break

            header = ur.AttrMap(ur.Columns(
                [("pack", post_info), ("pack", reply_btn)], 1), "reverse")

            thread_buf = [header, op["text"], self.parent.div]
            thread_buf.extend(replies)
            thread_list.extend(thread_buf)

        body = ur.ListBox(thread_list)
        if len(thread_list) > 0:
            body.set_focus(0)

        self.loop.Widget = ur.Frame(
            body, self.parent.header, self.parent.footer, "body")

    def print_thread(self, button, thread):
        thr_no = self.board.thread_exists(int(thread))
        thr_body = self.board.get_index()[thr_no]
        replies = ur.SimpleFocusListWalker([])

        subject = ("reverse_red", thr_body[1])
        if subject[1] == "":
            subject = (None, "")

        op = self.parse_post(thr_body[2])
        op_info = ur.Text([("reverse_green", op["name"]),
                           " " + op["stamp"] + " ", subject])
        op_btn = CleanButton(
            "No. " + op["id"], self.reply_box, op["id"])

        op_widget = ur.AttrMap(ur.Columns(
            [("pack", op_info), ("pack", op_btn)], 1), "reverse")

        replies.extend([op_widget, op["text"], self.parent.div])

        if len(thr_body) > 3:
            for postno in range(3, len(thr_body)):
                reply = self.parse_post(thr_body[postno])

                reply_info = ur.Text(
                    [("green", reply["name"]), " " + reply["stamp"]])
                reply_btn = CleanButton(
                    "No. " + reply["id"], self.reply_box, reply["id"])

                reply_widget = ur.Columns(
                    [("pack", reply_info), ("pack", reply_btn)],
                    1)

                replies.extend([reply_widget, reply["text"], self.parent.div])

        contents = ur.ListBox(replies)
        contents.set_focus(0)

        self.loop.Widget = ur.Frame(
            contents, self.parent.header, self.parent.footer, "body")

    def reply_box(self, button, thr_id):
        subject = ur.Edit(("blue", "Subject: "), wrap="clip")
        name = ur.Edit(("blue", "Name: "), "Anonymous", wrap="clip")
        if thr_id == -1:
            text = ur.Edit(multiline=True)
        else:
            text = ur.Edit(edit_text=">>" + thr_id, multiline=True)
        post_btn = ur.AttrMap(ur.Button(
            "Post", self.add_post, (subject, name, text, thr_id)),
            "green", "b_green")

        box = ur.LineBox(ur.ListBox(ur.SimpleFocusListWalker(
            [name, subject, ur.LineBox(text, "Post text"),
             self.parent.div, post_btn])))

        self.loop.Widget = MyOverlay(
            box, self.loop.baseWidget,
            "center", ("relative", 100), "top", ("relative", 100),
            None, None,
            self.parent.margin, self.parent.margin,
            int(self.loop.dimensions[1] * 0.3),
            int(self.loop.dimensions[1] * 0.3),
            self.parent)

    def add_post(self, button, data):
        # TODO: posting.
        logging.debug("data=%s", data[2].edit_text)

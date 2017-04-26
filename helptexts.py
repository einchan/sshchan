"""All the long and ugly-looking helptexts go here."""
from config import Colors as c
from chan_mark import Marker as marker

admin_helptext = \
c.RED + "sshchan-admin help\n" \
+ c.GREEN + "add" + c.YELLOW + " [name] [description]\n" \
+ c.BLACK + "adds a board with [name] and [description]\n\
don't use slashes, they're added automatically.\n" \
+ c.GREEN + "config" + c.YELLOW + " [option] [new value]\n" \
+ c.BLACK + "changes [option]'s value to [new value] in the sshchan.conf config file.\n" \
+ c.GREEN + "list|ls\n" \
+ c.BLACK + "lists boards\n" \
+ c.GREEN + "lsconfig\n" \
+ c.BLACK + "lists current configuration options\n" \
+ c.GREEN + "rename" + c.YELLOW + " [name] [new description]\n" \
+ c.BLACK + "changes the description of board [name] to [new description]\n" \
+ c.GREEN + "rm" + c.YELLOW + " [board] [post no.]\n" \
+ c.BLACK + "removes the post with post no. on board\n" \
+ c.GREEN + "rmboard" + c.YELLOW + " [name]\n" \
+ c.BLACK + "deletes board [name]\n" \
+ c.GREEN + "exit\n" \
+ c.BLACK + "exits sshchan-admin"

display_legacy_helptext = \
{"exit": ["exit | q | quit", "",  "Quits sshchan. Takes no arguments."],\
 "help": ["h | help", "[] | [command]", "Prints a help message."],\
 "cd": ["b | board | cd", "[board name]", "Displays the given board."],\
 "page": ["p | page", "[page no.]", "Choose which page of a board to display."],\
 "view": ["v | view", "[thread/post no.]", "Displays a thread."],\
\
 "re": ["re | reply", "[board name] | [[thread no.] [[text]]]",\
 "Replies to a thread or creates a new one.\n\
sshchan/board/> re " + c.GREEN + "# Posts a new thread to /board/\n" \
+ c.BLACK + "sshchan/board/> re 1 " + c.GREEN + "# Replies to thread no.1\n" \
+ c.BLACK + "sshchan/board/1> re " + c.GREEN + \
"# Replies to thread no.1 with the given text." + c.BLACK \
],\
 "refresh": ["refresh | rb", "", "Refreshes the current board."],\
 "rt": ["rt", "", "Refreshes the current thread."],\
}

markup_helptext = \
c.PURPLE + "\nMarkup help:\n" + c.BLACK + \
"\'\'\'text\'\'\' ---> " + "\033[1mtext\033[0m [bold]\n" + \
"~~text~~ -----> " + "\033[9mtext\033[0m [strikethrough]\n" + \
"==text== -----> " + "\033[7mtext\033[0m [reverse video]"

display_legacy_userguide = \
c.YELLOW + "sshchan: " + c.BLACK + "a user's guide\n" + \
"When you first enter sshchan, you'll see a command prompt like this:\n" + \
c.BLUE + "\tsshchan///>\n\n" + c.BLACK + \
"Those slashes are significant. They show you where you are on the chan according \
to this scheme:\n" + \
c.BLUE + "\tsshchan/" + c.YELLOW + "[BOARD]" + c.BLUE + "/" + \
c.YELLOW + "[THREAD NO.]" + c.BLUE + "/>\n\n" + \
c.BLACK + "Use the \'cd\' command to go to different boards:\n" + \
c.BLUE + "\tsshchan///>" + c.BLACK + " cd /meta/\n" + \
c.YELLOW + "\t***displays threads on the board***\n" + \
c.BLUE + "\tsshchan/meta//>\n\n" + \
c.BLACK + "One can refresh the current board with the \'refresh\' command:\n" + \
c.BLUE + "\tsshchan/meta//> " + c.BLACK + "refresh\n\n" + \
"You can go to a thread with the \'v\' command:\n" + \
c.BLUE + "\tsshchan/meta//>" + c.BLACK + " v 1\n" + \
c.YELLOW + "\t***displays thread no.1***\n" + \
c.BLUE + "\tsshchan/meta/" + c.PURPLE + "1" + c.BLUE + "/>\n\n" + \
c.BLACK + "This shows you the thread. Or, if you put in a reply's post number, it will show \
the thread from which that reply came.\n"


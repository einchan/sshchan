"""
Markup class allows the use of easy-to-write characters to style the text
instead of using escape codes.

==text== --> reverse video
'''text''' --> bold
~~text~~ --> strikethrough

Copyright (c) 2015
makos <https://github.com/makos>, chibi <http://neetco.de/chibi>
under GNU GPL v2, see LICENSE for details
"""

import re
import string

class Marker():

    def esc(self, input_text):
        output_text = ''
        for c in input_text:
            if c not in string.printable + string.whitespace:
                output_text += '\\' + str(ord(c))
            else:
                output_text += c
        return output_text

    def demarkify(self, input_text):
        """Prints out a marked-up piece of text."""
        output_text = self.esc(input_text)
        # strikethrough
        output_text = re.sub(
            '~~(?P<substring>.*?)~~', '\033[0;9m\g<substring>\033[0m',
            output_text)
        # bold
        output_text = re.sub(
            '\'\'\'(?P<substring>.*?)\'\'\'', '\033[0;1m\g<substring>\033[0m',
            output_text)
        # rv
        output_text = re.sub(
            '==(?P<substring>.*?)==', '\033[0;7m\g<substring>\033[0m',
            output_text)

        return output_text

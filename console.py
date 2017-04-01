"""
console.py
Adam Weidner 2012

Do whatever you want with it, really, go ahead.

Tab completion code copied from Stack Overflow
user http://stackoverflow.com/users/897150/trcx
"""
import readline
import getpass
import sys


class Console:

    def __init__(self, prompt=">>> "):
        """Initialize the prompt, that's about it"""
        self.prompt = prompt
        # automatically use the correct input version in python versions 2 and
        # 3
        if (sys.version_info > (3, 0)):
            self.get_input = input
        else:
            self.get_input = raw_input

    def console(self,
                prompt=None,
                default=None,
                autocomplete=None,
                password=False,
                intro=None,
                valid=lambda x: True):
        """
        console is the main function that you call to start interaction.
        The arguments are as follows:
            -prompt: A string that specifies what the prompt text is
            -default: Specify a default choice
            -autocomplete: Enable autocomplete for this / specify a list of
                autocomplete items
            -password: Set to true to have the input be set to password
            -intro: Give an intro message
            -valid: Give some validation

        Any of these arguments can be set with the setters and getters as well
        """

        # It makes sense that we would want to reuse the prompt, so
        # check to see if that's already set.  Additionally,
        # we are implicitly reusing autocomplete
        if not prompt:
            prompt = self.prompt

        # Print the intro first
        if intro:
            print(intro)

        # If it's password input, take care of it with getpass
        if password:
            while True:
                user_input = getpass.getpass(prompt)
                if valid and valid(user_input):
                    break
        else:
            # Set the autocompletion if it's enabled for this
            if autocomplete:
                if isinstance(autocomplete, list):
                    self.autocomplete(autocomplete)
                readline.parse_and_bind("tab: complete")
                readline.set_completer(self.complete)

            # Bake in validity testing
            while True:
                user_input = self.get_input("%s" % (prompt))
                if not user_input and default:
                    user_input = default
                if valid(user_input):
                    break
        return user_input

    def autocomplete(self, commands):
        """Set the commands that are allowed to autocomplete on tab"""
        self.commands = commands

    def complete(self, text, state):
        """The completion function for use by readline"""
        for option in self.commands:
            if option.startswith(text):
                if not state:
                    return option
                else:
                    state -= 1


def main():
    # Example usages
    c = Console(">>> ")
    c.autocomplete(["hello", "helle", "test", "testing", "goodbye", "boat"])
    result = c.console(intro="Welcome to the console!\n", autocomplete=True)

    print("The result was %s" % result)

    password = c.console(prompt="Enter a password: ", password=True)

    print("The password is %s" % password)

    valid = c.console(prompt="Enter a number less than 100: ",
                      valid=valid_test_example)

    print("Input %s was valid" % str(valid))

    default = c.console(
        prompt="Enter a value [Hello world]: ", default="Hello world")

    print("The value was %s" % default)


def valid_test_example(x):
    if int(x) < 100:
        return True
    else:
        print("Invalid input")
        return False

if __name__ == "__main__":
    main()

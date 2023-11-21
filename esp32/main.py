# OTA

import sys

from machine import Pin
from src.oled import oled
import os
import time


boot_button = Pin(0, Pin.IN, Pin.PULL_UP)
# buttons init
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)

b0_prev = button0.value()
b1_prev = button1.value()


def is_directory(path):
    try:
        # Get file/directory information
        stat_info = os.stat(path)

        # Check if it is a directory
        return stat_info[0] & 0o170000 == 0o040000  # S_IFDIR
    except OSError as e:
        # Handle the case where the path doesn't exist or there is an error
        return False


class BootMenu:

    def __init__(self):
        # for tracking the direction and button state

        self.previous_value = True
        self.button_down = False

        # Screen Variables
        self.width = 128
        self.height = 64
        self.line = 1
        self.highlight = 1
        self.shift = 0
        self.list_length = 0
        self.total_lines = 6

    def get_items(self):
        files = os.listdir()
        menu = []
        for file in files:
            if file.endswith(".py"):
                menu.append(file)
            # else:
            #     menu.append(file)
        menu.append('WebREPL')
        menu.append('REPL')

        return (menu)

    def show_menu(self, menu):
        """ Shows the menu on the screen"""

        # menu variables
        item = 1
        self.line = 1
        line_height = 10

        # clear the display
        oled.fill_rect(0, 0, self.width, self.height, 0)

        # Shift the list of files so that it shows on the display
        self.list_length = len(menu)
        short_list = [f.replace('.py', '') for f in menu[self.shift:self.shift + self.total_lines]]
        print(menu)
        for item in short_list:
            if self.highlight == self.line:
                oled.fill_rect(0, (self.line - 1) * line_height, self.width, line_height, 1)
                oled.text(">", 0, (self.line - 1) * line_height, 0)
                oled.text(item, 10, (self.line - 1) * line_height, 0)
                oled.show()
            else:
                oled.text(item, 10, (self.line - 1) * line_height, 1)
                oled.show()
            self.line += 1
        oled.show()

    def launch(self, filename):
        """ Launch the Python script <filename> """
        # clear the screen
        if filename == "REPL":
            oled.fill(0)
            oled.text('REPL>_', 40, 20)
            oled.show()
            sys.exit()

        elif filename == "WebREPL":
            from src import wrepl
            assert wrepl
            sys.exit()

        elif is_directory(filename):
            os.chdir(filename)
            items = self.get_items()
            self.show_menu(items)

        else:

            oled.fill_rect(0, 0, self.width, self.height, 0)
            oled.text("Launching", 1, 10)
            oled.text(filename, 1, 20)
            oled.show()
            # sleep(3)
            exec(open(filename).read())
            self.show_menu(self.file_list)
            return 0

    def run(self):

        b0_prev = button0.value()
        b1_prev = button1.value()

        # Get the list of Python files and display the menu
        self.file_list = self.get_items()
        self.show_menu(self.file_list)

        while True:
            b0_val = not button0.value()
            b1_val = not button1.value()

            if b0_prev != button0.value():
                b0_prev = button0.value()
                if b0_val:
                    self.file_list.append(self.file_list.pop(0))
                    self.show_menu(self.file_list)

            if b1_prev != button1.value():
                b1_prev = button1.value()

                if b1_val:
                    self.launch(self.file_list[(self.highlight - 1) + self.shift])

            time.sleep(0.1)

try:
    if not button0.value():
        boot_menu = BootMenu()
        boot_menu.run()
    else:
        import run

except (Exception, KeyboardInterrupt) as exc:
    print("FATAL: ", exc)
    # is_rem_run = input("Remove broken run.py?")
    # if is_rem_run == 'yes':
    #     import os
    #     os.remove('run.py')

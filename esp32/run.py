import time
from machine import UART, I2C, Pin
import ssd1306
import _thread
import parser
# import freesans20
import courier20
import font10
from writer import Writer


# buttons init
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)
boot_button = Pin(0, Pin.IN, Pin.PULL_UP)


# oled init
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


class Switch:
    cmd_list = tuple(parser.RequestBuilder.keys())

    def __init__(self):
        self._idx = 0
        self.cmd = self.cmd_list[self._idx]

    def next(self):
        self._idx += 1
        if self._idx == len(self.cmd_list):
            self._idx = 0
        self.cmd = self.cmd_list[self._idx]

    def __str__(self):
        return parser.CMD_STR[self.cmd]


class OLEDLines:
    lines = [""] * 3

    def clear(self):
        self.lines = [""] * 3

    def oled_upd(self):
        oled.fill(0)
        # oled.text(f"{switch}", 0, 0)

        wri = Writer(oled, font10)
        wri.set_textpos(oled, 0, 0)
        wri.printstring(f"{switch}")

        oled.text(f"{self.lines[0]}", 0, 25)
        oled.text(f"{self.lines[1]}", 0, 35)
        oled.text(f"{self.lines[2]}", 0, 45)
        # oled.text(f"{self.lines[3]}", 0, 50)
        oled.show()


def read_uart():
    while not QUIT:
        data = uart.read(1)
        if data == b'\xee':
            time.sleep(0.1)
            _d = uart.read(2)
            if _d:
                len_eq = bytearray(_d)
                expected_length = len_eq[1] + 1
                data += len_eq
                data += uart.read(expected_length)

                print('resp', data)

                try:
                    cmd, resp_data = parser.response_unpack(bytearray(data))
                    print(cmd, resp_data)

                    if cmd in [0x02, 0x04]:
                        wri = Writer(oled, font10)
                        wri.set_textpos(oled, 30, 10)
                        wri.printstring(f"{resp_data['d']}m")
                        oled.show()
                    else:
                        lines = parser.FMT[cmd].format(**resp_data)
                        for i, line in enumerate(lines.split('\n')):
                            oled_lines.lines[i] = line
                        oled_lines.oled_upd()

                except Exception as exc:
                    print(exc)
                    oled_lines.lines[1] = "> UndefErr"
                    oled_lines.oled_upd()

        elif data == b'' or not data:
            pass
        else:
            print('resp', data)

        time.sleep(0.2)


def show_hello():
    wri = Writer(oled, courier20)
    wri.set_textpos(oled, 0, 22)
    wri.printstring('ARCHER')

    wri1 = Writer(oled, font10)
    wri1.set_textpos(oled, 28, 20)
    wri1.printstring("InfiRay-LRF")

    # oled.text("InfiRay-LRF", 20, 30)
    # oled.text("tester", 40, 40)
    oled.text("by o-murphy", 18, 50)
    oled.show()
    time.sleep(2)


def show_repl():
    oled.fill(0)

    wri = Writer(oled, courier20)
    wri.set_textpos(oled, 20, 22)
    wri.printstring("AMPY>_")

    # oled.text("AMPY>_", 40, 10)
    oled.show()


with open('bootmode', 'rb') as fp:
    bootmode = fp.read()


if bootmode == b'\x01':

    lrf_en = Pin(2, Pin.OUT)
    lrf_en.on()

    # uart1 init
    uart = UART(1, baudrate=115200, tx=Pin(17), rx=Pin(16))

    QUIT = False
    show_hello()
    switch = Switch()
    oled_lines = OLEDLines()
    oled_lines.oled_upd()
    _thread.start_new_thread(read_uart, ())

    while True:

        b0 = not button0.value()
        b1 = button1.value()

        if b0:
            oled.fill(0)
            print(">> cmd", switch.cmd)
            req = parser.request_pack(switch.cmd)
            uart.write(req)
            oled_lines.clear()
            oled_lines.lines[0] = f"> {switch}"
            oled_lines.oled_upd()

        if b1:
            switch.next()
            oled_lines.oled_upd()

        if boot_button.value() == 0:
            QUIT = True

            show_repl()
            with open('bootmode', 'wb') as fp:
                fp.write(b'\x00')
            time.sleep(0.1)
            # reset()

        time.sleep(0.2)

else:
    show_repl()
    with open('bootmode', 'wb') as fp:
        fp.write(b'\x01')

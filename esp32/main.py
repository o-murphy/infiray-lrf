import time
from machine import UART, I2C, Pin
import ssd1306
import _thread
import parser


# buttons init
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)

# uart1 init
uart = UART(1, baudrate=115200, tx=Pin(17), rx=Pin(16))


# oled init
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


QUIT = False


class Switch:
    cmd_list = tuple(parser.CMD_STR.keys())

    def __init__(self):
        self._idx = 0x01
        self.cmd = 0x01

    def next(self):
        self._idx += 1
        if self._idx == len(self.cmd_list):
            self._idx = 0
        self._idx = self.cmd_list[self._idx]

    def __str__(self):
        return parser.CMD_STR[self._idx]


w_out = ""
r_out = ""


switch = Switch()


def oled_upd():
    oled.fill(0)
    oled.text(f"C: {switch}", 10, 0)
    oled.text(f"W: {w_out}", 10, 10)
    oled.text(f"R: {r_out}", 10, 20)
    oled.show()


def read_uart():
    global r_out
    while not QUIT:
        data = uart.read(1)
        if data == b'\xee':
            time.sleep(0.2)
            _d = uart.read(2)
            if _d:
                len_eq = bytearray(_d)
                expected_length = len_eq[1] + 1
                data += len_eq
                data += uart.read(expected_length)

                print('resp', data)
                r_out = str(data)
                oled_upd()

                try:
                    resp_data = parser.response_unpack(bytearray(data))
                    print(resp_data)
                except Exception:
                    print("Parsing error")

        elif data == b'' or not data:
            pass
        else:
            print('resp', data)

        time.sleep(0.2)


_thread.start_new_thread(read_uart, ())

while True:

    b0 = not button0.value()
    b1 = button1.value()

    if b0:
        oled.fill(0)
        print("req", 0x02)
        req = parser.request_pack(0x02)
        w_out = uart.write(req)
        oled_upd()

    if b1:
        switch.next()
        oled_upd()

    time.sleep(0.1)


#  b'\xee\x16\x06\x03\x02\x00\x00\r\x07\x19'
#  b'\xee\x16\x06\x03\x02\x00\x00\r\x01\x13'
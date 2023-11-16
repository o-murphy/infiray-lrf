import time
from machine import UART, I2C, Pin
import ssd1306
import _thread
import parser


# buttons init
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)
boot_button = Pin(0, Pin.IN, Pin.PULL_UP)

lrf_en = Pin(2, Pin.OUT)
lrf_en.on()

# uart1 init
uart = UART(1, baudrate=115200, tx=Pin(17), rx=Pin(16))


# oled init
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


QUIT = False


oled.text("ARCHER", 40, 10)
oled.text("InfiRay-LRF", 20, 20)
oled.text("tester", 40, 30)
oled.text("by o-murphy", 20, 50)
oled.show()
time.sleep(1)


class Switch:
    cmd_list = tuple(parser.RequestBuilder.keys())

    def __init__(self):
        self._idx = 0x01
        self.cmd = 0x01

    def next(self):
        self._idx += 1
        if self._idx == len(self.cmd_list):
            self._idx = 0
        self.cmd = self.cmd_list[self._idx]

    def __str__(self):
        return parser.CMD_STR[self.cmd]


class OLEDLines:
    lines = [""] * 4

    def clear(self):
        self.lines = [""] * 4

    def oled_upd(self):
        oled.fill(0)
        oled.text(f"{switch}", 0, 0)
        oled.text(f"{self.lines[0]}", 0, 10)
        oled.text(f"{self.lines[1]}", 0, 20)
        oled.text(f"{self.lines[2]}", 0, 30)
        oled.text(f"{self.lines[3]}", 0, 40)
        oled.show()


switch = Switch()
oled_lines = OLEDLines()


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
                    lines = parser.FMT[cmd].format(**resp_data)
                    for i, line in enumerate(lines.split('\n')):
                        oled_lines.lines[i] = line

                except Exception as exc:
                    print(exc)
                    oled_lines.lines[1] = ">> Error"
                oled_lines.oled_upd()

        elif data == b'' or not data:
            pass
        else:
            print('resp', data)

        time.sleep(0.2)


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
        oled_lines.lines[0] = f">> {parser.CMD_STR[switch.cmd]}"
        oled_lines.oled_upd()

    if b1:
        switch.next()
        oled_lines.oled_upd()

    if boot_button.value() == 0:
        QUIT = True
        oled.fill(0)
        oled.text("REPL>_", 40, 10)
        oled.show()
        time.sleep(0.1)
        break

    time.sleep(0.2)

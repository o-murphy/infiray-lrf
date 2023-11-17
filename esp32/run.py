import time
from machine import UART, Pin
import sys
import _thread
from src import parser
from src.fonts import courier20, freesans20, font6, font10
from src.oled import *

# buttons init
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)
boot_button = Pin(0, Pin.IN, Pin.PULL_UP)

lrf_en = Pin(2, Pin.OUT)
uart = UART(1, baudrate=115200, tx=Pin(17), rx=Pin(16))


def exit_to_repl():
    lrf_en.off()
    oled.fill(0)
    oled.text('REPL>_', 40, 20)
    oled.show()
    sys.exit()


def bootmode():
    try:
        with open('bootmode', 'rb') as fp:
            if fp.read() == b'\x01':
                return
            else:
                raise Exception
    except Exception:
        oled.fill(0)
        oled.text("autorun disabled", 0, 10)
        oled.text("select boot mode", 0, 20)
        oled.show()
        c, s = 0, 0.5
        # led.value(1)
        while True:
            if not boot_button.value():
                while not boot_button.value():
                    if c >= 2:
                        try:
                            with open('bootmode', 'wb') as fp:
                                fp.write(b'\x00')
                        except Exception:
                            pass
                        exit_to_repl()
                    time.sleep(s / 2)
                    # led.value(1)
                    time.sleep(s / 2)
                    # led.value(0)
                    c += s
                try:
                    with open('bootmode', 'wb') as fp:
                        fp.write(b'\x01')
                except Exception:
                    pass
                return
            time.sleep(0.1)


# class Switch:
#     cmd_list = tuple(parser.RequestBuilder.keys())
#
#     def __init__(self):
#         self._idx = 0
#         self.cmd = self.cmd_list[self._idx]
#
#     def next(self):
#         self._idx += 1
#         if self._idx == len(self.cmd_list):
#             self._idx = 0
#         self.cmd = self.cmd_list[self._idx]
#
#     def __str__(self):
#         return parser.CMD_STR[self.cmd]


def read_uart():
    while not QUIT:
        data = uart.read(1)
        if data == b'\xee':
            time.sleep(0.01)
            _d = uart.read(2)
            if _d:
                len_eq = bytearray(_d)
                expected_length = len_eq[1] + 1
                data += len_eq
                data += uart.read(expected_length)

                # print('resp', data)  # uncomment on need

                try:
                    cmd, resp_data = parser.response_unpack(bytearray(data))
                    # print(cmd, resp_data)  # uncomment on need

                    if cmd in [0x02, 0x04]:
                        on_result(f"{resp_data['d']}m\t\t")
                        oled.show()

                    elif cmd == 0x06:
                        on_result(f"Err:0x{resp_data['status']:02X}\t\t")
                        oled.show()

                    elif cmd == 0x05:
                        pass

                    # else:
                    #     lines = parser.FMT[cmd].format(**resp_data)
                    #     text(lines, 0, 25, font=font10)

                except Exception as exc:
                    print(exc)
                    on_result("Undef")

        elif data == b'' or not data:
            pass
        else:
            # print('resp', data)  # uncomment on need
            pass

        time.sleep(0.02)


def show_hello():
    text('ARCHER', 22, 0, font=courier20)
    text("InfiRay-LRF", 20, 28, font=font10)
    oled.text("by o-murphy", 18, 50)
    oled.show()
    time.sleep(2)


def spin(spinner, idx=None):
    if idx:
        spinner.idx = idx
    text(f"{spinner.next()}", 0, (oled_height - freesans20.height()) // 2, False, freesans20)
    oled.show()


def on_state(state):
    text(state, 0, 0, font=font6)
    oled.show()


def on_result(result):
    text(result, 50, (oled_height - freesans20.height()) // 2, False, freesans20)
    oled.show()


class Spinner:
    # states = "\/-"
    _states = ["===", ">==", ">>=", ">>>", "=>>", "==>",
               "===", "==<", "=<<", "<<<", "<<=", "<=="]

    def __init__(self, idx=0, states=None):
        self.idx = idx
        self.states = states if states else self._states

    def next(self):
        self.idx += 1
        if self.idx == len(self.states):
            self.idx = 0
        return self.states[self.idx]


def set_lrf_frequency():
    uart.write(b'\xee\x16\x04\x03\xa1\n\x00\xae')  # frequency 10
    # uart.write(b'\xee\x16\x04\x03\xa1\x05\x00\xa9')  # frequency 5
    # uart.write(b'\xee\x16\x04\x03\xa1\x02\x00\xa6')  # frequency 2
    # uart.write(b'\xee\x16\x04\x03\xa1\x01\x00\xa5')  # frequency 1
    time.sleep(0.25)


bootmode()
# led.value(0)
oled.fill(0)

# print('lrf pin', lrf_en.value())
lrf_en.on()
# print('lrf pin', lrf_en.value())

show_hello()

QUIT = False

b1_prev = button1.value()
b0_prev = button0.value()
scan_spinner = Spinner()
range_spinner = Spinner(states=["===", ">=<", "=x=", ])

oled.fill(0)
rect(40, 14, 128, 50)
hline(font6.height() - 1, 0, oled_width)
spin(range_spinner, -1)
on_state(">_ stopped ")

oled.show()

_thread.start_new_thread(read_uart, ())

set_lrf_frequency()

while True:
    c, s = 0, 0.5
    while not boot_button.value():
        on_state(">_ mode")
        if c >= 2:
            QUIT = True
            try:
                with open('bootmode', 'wb') as fp:
                    fp.write(b'\x00')
            except Exception:
                pass
            exit_to_repl()
        c += s
        time.sleep(s)

    if c > 0:
        if lrf_en.value() == 0:
            lrf_en.on()
            time.sleep(0.25)
            set_lrf_frequency()
            on_result(f"LRF:ON\t\t")
            on_state(">_ stopped\t")
        else:
            lrf_en.off()
            on_result(f"LRF:OFF\t\t")
            on_state(">_ disabled")
        oled.show()

    if b0_prev != button0.value():
        if button0.value():
            b0_prev = button0.value()
            # print('0', b0_prev)
            on_state(">_ ranging\t")

            uart.write(parser.request_pack(0x02))

            for i in range(len(range_spinner.states)):
                spin(range_spinner)
                time.sleep(0.1)
                oled.show()
            spin(range_spinner, -1)
            on_state(">_ stopped\t")
        else:
            b0_prev = button0.value()

    b1_val = not button1.value()

    if b1_prev != button1.value():
        b1_prev = button1.value()
        # print('1', b1_prev)
        if not b1_val:

            uart.write(parser.request_pack(0x04))

            on_state(">_ scanning")
        else:
            uart.write(parser.request_pack(0x05))

            on_state(">_ stopped\t")
            spin(scan_spinner, -1)

    if not b1_val:
        spin(scan_spinner)

    oled.show()
    time.sleep(0.02)

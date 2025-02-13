# OTA

from machine import UART, Pin
import _thread
from src import parser
from src.fonts import courier20, freesans20, font6, font10
from src.oled import *
import time
# from src.bootmode import *


boot_button = Pin(0, Pin.IN, Pin.PULL_UP)
# buttons init
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)

lrf_en = Pin(2, Pin.OUT)
uart = UART(1, baudrate=115200, tx=Pin(16), rx=Pin(17))


# def exit_to_repl():
#     lrf_en.off()
#     bootmode_repl(oled)


def read_uart():
    global ERR_COUNT
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
                        on_result(f"{resp_data['d']}m")

                    elif cmd == 0x06:
                        on_result(f"Err:x{resp_data['status']:02X}")
                        ERR_COUNT += 1
                        on_status(f"{resp_data['mask']} err: {ERR_COUNT}")

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
    oled.fill(0)
    text('ARCHER', 22, 0, font=courier20)
    text("InfiRay-LRF", 20, 28, font=font10)
    oled.text("by o-murphy", 18, 50)
    oled.show()
    time.sleep(2)


def spin(spinner, idx=None):
    draw_spin_rect()
    if idx:
        spinner.idx = idx
    text(f"{spinner.next()}", 0, (oled_height - freesans20.height()) // 2, False, freesans20)
    oled.show()


def on_state(state):
    draw_top_rect()
    text(state, 0, 0, font=font6)
    oled.show()


def on_result(result):
    draw_range_rect()
    text(result, 50, (oled_height - freesans20.height()) // 2, False, freesans20)
    oled.show()


def on_status(status):
    draw_bottom_rect()
    oled.text(status, 0, oled_height-13)
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


# bootmode(oled)
lrf_en.on()
show_hello()

# init globalvars
QUIT = False
ERR_COUNT = 0
b1_prev = button1.value()
b0_prev = button0.value()
scan_spinner = Spinner()
range_spinner = Spinner(states=["===", ">=<", "=x=", ])

# init gui
oled.fill(0)
oled.rect(40, 14, 88, 36, 1)
oled.hline(0, font6.height(), oled_width, 1)
oled.hline(0, oled_height-font6.height()-1, oled_width, 1)
draw_range_rect()
draw_top_rect()
draw_bottom_rect()
spin(range_spinner, -1)
on_state(">_ stopped ")

# start uart read thread
_thread.start_new_thread(read_uart, ())

# set lrf frequency
set_lrf_frequency()

while True:
    c, s = 0, 0.5
    while not boot_button.value():
        on_state(">_ mode")
        if c >= 2:
            QUIT = True
            # disable_autoboot()
            # exit_to_repl()
        c += s
        time.sleep(s)

    if c > 0:
        if lrf_en.value() == 0:
            lrf_en.on()
            time.sleep(0.25)
            set_lrf_frequency()
            on_result(f"LRF:ON")
            on_state(">_ stopped")
        else:
            lrf_en.off()
            on_result(f"LRF:OFF")
            on_state(">_ disabled")

    if b0_prev != button0.value():
        if button0.value():
            b0_prev = button0.value()

            on_state(">_ ranging")

            uart.write(parser.request_pack(0x02))

            for i in range(len(range_spinner.states)):
                spin(range_spinner)
                time.sleep(0.1)

            spin(range_spinner, -1)
            on_state(">_ stopped")
        else:
            b0_prev = button0.value()

    b1_val = not button1.value()

    if b1_prev != button1.value():
        b1_prev = button1.value()

        if not b1_val:

            uart.write(parser.request_pack(0x04))

            on_state(">_ scanning")
        else:
            uart.write(parser.request_pack(0x05))

            on_state(">_ stopped")
            spin(scan_spinner, -1)

    if not b1_val:
        spin(scan_spinner)

    time.sleep(0.02)

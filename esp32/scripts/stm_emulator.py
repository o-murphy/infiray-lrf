import struct
from machine import UART, Pin
import _thread
from src.oled import *
from src.fonts import freesans20, font6
import time
import random


boot_button = Pin(0, Pin.IN, Pin.PULL_UP)
# buttons init
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)


lrf_en = Pin(2, Pin.OUT)
uart = UART(1, baudrate=115200, tx=Pin(17), rx=Pin(16))


CMD_STR = {
    0x01: 'Self Inspection',
    0x02: 'Single Ranging',
    0x04: 'Scanning',
    0x05: 'Stop Scanning',
    0x06: 'Ranging Error',
}

FMT = {
    0x01: '> Insp:',
    0x02: '> Range: {d}m\nStatus: {s}',
    0x04: '> Range: {d}m\nStatus: {s}',
    0x05: '> Stopped',
    0x06: '> Ranging Error\nf{fp} l{lo} w{w} e{ec}\nt{t} bs{bs} bo{bo}',
}


def crc(data):
    return sum(data[3:-1]) & 0xFF


def range_resp_pack(status, range: float):
    r, d = int(range // 1), int(range % 1 * 10)
    return struct.pack(">BhB", status, r, d)


def continuous_resp_pack(status, range: float):
    r, d = int(range // 1), int(range % 1 * 10)
    return struct.pack(">BhB", status, r, d)


def range_abnormal_pack(*args, **kwargs):
    return b''


RequestBuilder = {
    0x02: range_resp_pack,
    0x04: continuous_resp_pack,
    0x05: lambda *args, **kwargs: {},
    0x06: range_abnormal_pack,
}

ResponseParser = {
    0x02: lambda *args: {},
    0x04: lambda *args: {},
    0x05: lambda *args: {},
}


def check_crc(data):
    return crc(data) == data[-1]


def response_unpack(data):
    hh, hl, ln, q, cmd = struct.unpack('<BBBBB', data[:5])
    if not check_crc(data):
        raise ValueError("Wrong CRC")
    if not cmd in ResponseParser:
        raise ValueError("Wrong CMD")
    func = ResponseParser[cmd]
    return cmd, func(data[5:-1])


def request_pack(cmd, **kwargs):
    data = bytearray(b'\xee\x16\xff\x03')
    data.append(cmd)

    if not cmd in RequestBuilder:
        raise ValueError("Wrong CMD")
    func = RequestBuilder[cmd]
    data.extend(func(**kwargs))
    data.append(0xff)
    data[2] = len(data) - 4
    data[-1] = crc(data)
    return data


def read_uart():
    global CONTINUE
    while True:
        data = uart.read(1)
        if data == b'\xee':
            time.sleep(0.01)
            _d = uart.read(2)
            if _d:
                len_eq = bytearray(_d)
                expected_length = len_eq[1] + 1
                data += len_eq
                data += uart.read(expected_length)
                print(data)

                try:
                    cmd, resp_data = response_unpack(bytearray(data))

                    on_state(f"GOT: {CMD_STR[cmd]}")

                    if cmd == 0x02:
                        _range = random_range()
                        # uart.write(request_pack(0x02, status=0, range=_range))
                        uart.write(str(_range).encode('ascii') + b'\n')
                        on_result(f"{_range}m")
                        on_status(f"Send: {CMD_STR[0x02]}")

                    elif cmd == 0x04:
                        CONTINUE = True
                        _thread.start_new_thread(continuous_ranging_emulate, ())

                    elif cmd == 0x06:
                        # on_result(f"Err:x{resp_data['status']:02X}")
                        # ERR_COUNT += 1
                        # on_status(f"{resp_data['mask']} err: {ERR_COUNT}")
                        ...

                    elif cmd == 0x05:
                        CONTINUE = False
                        uart.write(data)
                        on_result(f"Stop")
                        on_status(f"Send: {CMD_STR[0x02]}")

                except Exception as exc:
                    print(exc)
                    on_result("Undef")

        elif data == b'' or not data:
            pass
        else:
            pass

        time.sleep(0.02)


def continuous_ranging_emulate():

    while CONTINUE:
        _range = random_range()
        #uart.write(request_pack(0x02, status=0, range=_range))
        uart.write(str(_range).encode('ascii') + b'\n')
        on_result(f"{_range}m")
        on_status(f"Send: {CMD_STR[0x02]}")
        time.sleep(0.1)


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


def random_range():
    #return random.randrange(0, 30000, 1) / 10
    return random.randint(0, 3000)


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


# d = request_pack(0x02, status=0, range=60.5)  # Single ranging
# d = request_pack(0x04, status=0, range=60.5)  # Continuous ranging
# d = request_pack(0x05)  # Stop ranging

# cmd, res = response_unpack(data)
CONTINUE = False

# init gui
oled.fill(0)
oled.rect(40, 14, 88, 36, 1)
oled.hline(0, font6.height(), oled_width, 1)
oled.hline(0, oled_height-font6.height()-1, oled_width, 1)
draw_range_rect()
draw_top_rect()
draw_bottom_rect()

scan_spinner = Spinner()
range_spinner = Spinner(states=["===", ">=<", "=x=", ])
spin(range_spinner, -1)
# on_state(">_ stopped ")

on_state(f"No CMD")
on_result(f"None")
on_status(f"Idle")

read_uart()

# c = 0
# while 1:
#     print(c)
#     c += 1
#     _range = 19.0
#     d = request_pack(0x02, status=0, range=_range)
#     print(d)
#     uart.write(d)
#     on_result(f"{_range}m")
#     on_status(f"Send: {CMD_STR[0x02]}")
#     time.sleep(0.2)

from machine import UART, Pin
import _thread
from src.oled import *
from src.parser import *
import time
import random


# buttons init
boot_button = Pin(0, Pin.IN, Pin.PULL_UP)
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)

b0_prev = button0.value()
b1_prev = button1.value()


lrf_en = Pin(2, Pin.OUT)
uart = UART(1, baudrate=115200, tx=Pin(17), rx=Pin(16))


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


def continuous_ranging_emulate():

    while CONTINUE:
        _range = random_range()
        uart.write(request_pack(0x02, status=0, range=_range))
        on_result(f"{_range}m")
        on_status(f"Send: {CMD_STR[0x02]}")
        time.sleep(0.1)


def random_range():
    return random.randrange(0, 30000, 1) / 10


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

                try:
                    cmd, resp_data = response_unpack(bytearray(data))

                    on_state(f"GOT: {CMD_STR[cmd]}")

                    if cmd == 0x02:
                        _range = random_range()
                        uart.write(request_pack(0x02, status=0, range=_range))
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


show_hello()

# init gui
init_gui()

scan_spinner = Spinner()
range_spinner = Spinner(states=["===", ">=<", "=x=", ])
spin(range_spinner, -1)
on_state(f"No CMD")
on_result(f"None")
on_status(f"Idle")

CONTINUE = False
read_uart()

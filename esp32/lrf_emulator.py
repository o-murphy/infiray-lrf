import _thread
import random

from src.oled import *
from src.parser import *
from src.pinout import *


MessageBuilder = {
    0x02: range_resp_pack,
    0x04: continuous_resp_pack,
    0x05: lambda *args, **kwargs: {},
    0x06: range_abnormal_pack,
}


MessageParser = {
    0x02: lambda *args: {},
    0x04: lambda *args: {},
    0x05: lambda *args: {},
}


def continuous_ranging_emulate():
    while CONTINUE:
        _range = random_range()
        uart.write(message_pack(0x02, status=0, range=_range))
        on_result(f"{_range}m")
        on_status(f"Send: {CMD_STR[0x02]}")
        time.sleep(0.1)


def random_range():
    return random.randrange(0, 30000, 1) / 10


def on_command(data):
    global CONTINUE
    try:
        cmd, resp_data = message_unpack(bytearray(data))

        on_state(f"GOT: {CMD_STR[cmd]}")

        if cmd == 0x02:
            _range = random_range()
            uart.write(message_pack(0x02, status=0, range=_range))
            on_result(f"{_range}m")
            on_status(f"Send: {CMD_STR[0x02]}")

        elif cmd == 0x04:
            CONTINUE = True
            _thread.start_new_thread(continuous_ranging_emulate, ())

        elif cmd == 0x06:
            ...  # TODO

        elif cmd == 0x05:
            CONTINUE = False
            uart.write(data)
            on_result(f"Stop")
            on_status(f"Send: {CMD_STR[0x02]}")

    except Exception as exc:
        print(exc)
        on_result("Undef")


show_hello()

# init gui
init_gui()
scan_spinner = Spinner()
range_spinner = Spinner(states=["===", ">=<", "=x="])
spin(range_spinner, -1)
on_state(f"No CMD")
on_result(f"None")
on_status(f"Idle")

CONTINUE = False
read_uart(uart, on_command)

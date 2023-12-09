import random
import time


_FREQ = 125000000


def freq(value: int = None):
    global _FREQ
    if isinstance(value, int):
        _FREQ = value
    return _FREQ


class Pin:
    IN = ...
    OUT = ...

    def __init__(self, *args, **kwargs):
        ...

    def on(self):
        ...

    def off(self):
        ...


class UART:
    def __init__(self, *args, **kwargs):
        ...

    def read(self, n):
        time.sleep(0.02)
        if n == 1:
            return b'\xee'
        return random.randbytes(n)[:6]

    def write(self, data: bytes):
        time.sleep(0.02)
        return len(data)


class ADC:
    def __init__(self, *args, **kwargs):
        ...

    def read_u16(self):
        return random.randint(0, 65353)

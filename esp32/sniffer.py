from machine import UART, Pin
from src.oled import *
from src.fonts import freesans20, font6
import time


boot_button = Pin(0, Pin.IN, Pin.PULL_UP)
# buttons init
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)


lrf_en = Pin(2, Pin.OUT)
uart = UART(1, baudrate=115200, tx=Pin(16), rx=Pin(17))


def read_uart():
    global CONTINUE
    count = 0
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
                    count = 3
                    oled.fill(0)
                    text(f'{data.hex()}', 0, 5, False, font6)
                    oled.show()
                except Exception as exc:
                    print(exc)

        elif data == b'' or not data:
            pass
        else:
            pass

        time.sleep(0.02)
        if count > 0:
            count -= 0.02
        else:
            oled.fill(0)
            oled.show()


# cmd, res = response_unpack(data)
CONTINUE = False

# init gui
oled.fill(0)
oled.text(f'init sniffer', 0, 5)
oled.show()
read_uart()

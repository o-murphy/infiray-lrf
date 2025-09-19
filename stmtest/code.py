import time

import board
import busio
import digitalio

from lrfemu_min import random_range, request_pack

# defines
# led pins
LED_RED_PIN = board.GP21
LED_GREEN_PIN = board.GP22
LED_ACTIVE_HIGH = True

# btn pin
BTN_PIN = board.GP16

# uart pins
UART_0_TX_PIN = board.GP4
UART_0_RX_PIN = board.GP5
UART_1_TX_PIN = board.GP12
UART_1_RX_PIN = board.GP13

# packet pattern
CORE_TO_LRF_PACKET = b'\xee\x16\x04\x03\xa1\n\x00\xae'


class UniLED:
    def __init__(self, pin, active_high=True):
        self._pin = digitalio.DigitalInOut(pin)
        self._pin.direction = digitalio.Direction.OUTPUT
        self._active_high = active_high
        self.off()

    def on(self):
        self._pin.value = self._active_high

    def off(self):
        self._pin.value = not self._active_high


def format_bytes_as_hex(data):
    """Formats a byte string as a human-readable hex string."""
    return " ".join([f"{b:02X}" for b in data])


def loopback(uart_a, uart_b, data: bytes, timeout=0.5):
    uart_a.write(data)
    time.sleep(timeout)
    if uart_b.in_waiting > 0:
        received_data = uart_b.read(uart_b.in_waiting)
    else:
        received_data = b''
    received_data = received_data.strip().strip(b'\x00')
    return received_data


def core_to_lrf(uart_core, uart_lrf):
    "CORE_TO_LRF:"
    # packet = b'\xee' + bytes([random.randint(0, 255) for i in range(10)])
    print(f"uart_core sending: {format_bytes_as_hex(CORE_TO_LRF_PACKET)}")
    received_data = loopback(uart_core, uart_lrf, CORE_TO_LRF_PACKET)
    state = received_data == CORE_TO_LRF_PACKET
    print(f"uart_lrf received: {format_bytes_as_hex(received_data)}, {state=}\n")
    return state


def lrf_to_core(uart_lrf, uart_core):
    "LRF_TO_CORE:"
    _range = random_range()
    expected = str(int(_range // 1)).encode('ansi')
    packet = bytes(request_pack(0x02, status=0, range_=_range))
    print(f"uart_lrf sending:  {format_bytes_as_hex(packet)} ({_range})")
    received_data = loopback(uart_lrf, uart_core, packet)
    state = received_data == expected
    print(f"uart_core received: {received_data}, expected: {expected}, {state=}\n")
    return state


def check(uart_core, uart_lrf):
    led_red.off()
    led_green.off()

    time.sleep(0.5)

    status0 = core_to_lrf(uart_core, uart_lrf)
    time.sleep(0.1)
    status1 = lrf_to_core(uart_lrf, uart_core)
    status = status0 and status1

    led_green.on() if status else led_red.on()


# init pins
btn_pin = digitalio.DigitalInOut(BTN_PIN)
btn_pin.direction = digitalio.Direction.INPUT
btn_pin.pull = digitalio.Pull.UP

# Pin definitions for pins 6 and 7
# The RP2040 Zero board labels these as GP6 and GP7
led_red = UniLED(LED_RED_PIN, LED_ACTIVE_HIGH)
led_green = UniLED(LED_GREEN_PIN, LED_ACTIVE_HIGH)

# Create uart_core with transmit (TX) and receive (RX) pins.
# For Raspberry Pi Pico, TX is GP0 and RX is GP1.
uart_0 = busio.UART(UART_0_TX_PIN, UART_0_RX_PIN, baudrate=115200, timeout=1.0)  # Core side

# Create uart_lrf with transmit (TX) and receive (RX) pins.
# For Raspberry Pi Pico, TX is GP4 and RX is GP5.
uart_1 = busio.UART(UART_1_TX_PIN, UART_1_RX_PIN, baudrate=115200, timeout=1.0)  # LRF side

if __name__ == "__main__":
    print("Starting UART loopback test...")
    while True:
        if btn_pin.value == False:
            check(uart_0, uart_1)

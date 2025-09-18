import time

import board
import busio
import digitalio

from lrfemu import random_range, request_pack

# Pin definitions for pins 6 and 7
# The RP2040 Zero board labels these as GP6 and GP7
led6_red = digitalio.DigitalInOut(board.GP21)
led7_green = digitalio.DigitalInOut(board.GP22)

# Set the pins as outputs
led6_red.direction = digitalio.Direction.OUTPUT
led7_green.direction = digitalio.Direction.OUTPUT

btn_pin = digitalio.DigitalInOut(board.GP16)
btn_pin.direction = digitalio.Direction.INPUT
btn_pin.pull = digitalio.Pull.UP

# Create uart_core with transmit (TX) and receive (RX) pins.
# For Raspberry Pi Pico, TX is GP0 and RX is GP1.
uart_core = busio.UART(board.GP4, board.GP5, baudrate=115200, timeout=1.0)

# Create uart_lrf with transmit (TX) and receive (RX) pins.
# For Raspberry Pi Pico, TX is GP4 and RX is GP5.
uart_lrf = busio.UART(board.GP12, board.GP13, baudrate=115200, timeout=1.0)


def format_bytes_as_hex(data):
    """Formats a byte string as a human-readable hex string."""
    return " ".join([f"{b:02X}" for b in data])


def core_to_lrf():
    # CORE_TO_LRF:
    # packet = b'\xee' + bytes([random.randint(0, 255) for i in range(10)])
    packet = b'\xee\x16\x04\x03\xa1\n\x00\xae'
    print(f"uart_core sending: {format_bytes_as_hex(packet)}")
    uart_core.write(packet)  # Encode the string to bytes

    time.sleep(0.5)  # Small delay to allow data to be received

    # Check if there's any data available on uart_lrf
    if uart_lrf.in_waiting > 0:
        received_data = uart_lrf.read(uart_lrf.in_waiting)
    else:
        received_data = b''
    print(f"uart_lrf received: {format_bytes_as_hex(received_data)}")
    ret = received_data.strip().strip(b'\x00') == packet
    print("CORE_TO_LRF:", ret)
    print()
    return ret


def lrf_to_core():
    # LRF_TO_CORE:
    _range = random_range()
    _expected = str(int(_range // 1)).encode('ansi')
    packet = bytes(request_pack(0x02, status=0, range=_range))
    print(f"uart_lrf sending:  {format_bytes_as_hex(packet)} ({_range})")

    uart_lrf.write(packet)  # Encode the string to bytes

    time.sleep(0.5)  # Small delay to allow data to be received
    if uart_core.in_waiting > 0:
        received_data = uart_core.read(uart_core.in_waiting)
    else:
        received_data = b''
    print(f"uart_core received: {received_data}, expected: {_expected}")
    ret = received_data.strip().strip(b'\x00') == _expected
    print("LRF_TO_CORE:", ret)
    print()
    return ret


if __name__ == "__main__":
    print("Starting UART loopback test...")
    while True:
        if btn_pin.value == False:
            led6_red.value = False
            led7_green.value = False

            # status = core_to_lrf() and lrf_to_core()
            status0 = core_to_lrf()
            time.sleep(0.1)
            status1 = lrf_to_core()

            status = status0 and status1

            led7_green.value, led6_red.value = status, not status

            time.sleep(0.2)  # Wait for 2 seconds before the next message

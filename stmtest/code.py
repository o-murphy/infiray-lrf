import board
import digitalio
import busio
import time
from lrfemu import random_range, request_pack

# Pin definitions for pins 6 and 7
# The RP2040 Zero board labels these as GP6 and GP7
led6_red = digitalio.DigitalInOut(board.GP6)
led7_green = digitalio.DigitalInOut(board.GP7)

# Set the pins as outputs
led6_red.direction = digitalio.Direction.OUTPUT
led7_green.direction = digitalio.Direction.OUTPUT

# Create uart_core with transmit (TX) and receive (RX) pins.
# For Raspberry Pi Pico, TX is GP0 and RX is GP1.
uart_core = busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=1.0)

# Create uart_lrf with transmit (TX) and receive (RX) pins.
# For Raspberry Pi Pico, TX is GP4 and RX is GP5.
uart_lrf = busio.UART(board.GP4, board.GP5, baudrate=115200, timeout=1.0)

print("Starting UART loopback test...")

CORE_TO_LRF_MSG = b"Hello, RP2040!"


def core_to_lrf():
    # CORE_TO_LRF:
    print(f"uart_core sending: {CORE_TO_LRF_MSG}")
    uart_core.write(CORE_TO_LRF_MSG)  # Encode the string to bytes

    time.sleep(0.1)  # Small delay to allow data to be received

    # Check if there's any data available on uart_lrf
    if uart_lrf.in_waiting > 0:
        received_data = uart_lrf.read(uart_lrf.in_waiting)
    else:
        received_data = b''
    print(f"uart_lrf received: {received_data}")
    print("CORE_TO_LRF:", received_data == CORE_TO_LRF_MSG)
    return received_data == CORE_TO_LRF_MSG


def lrf_to_core():
    # LRF_TO_CORE:
    print(f"uart_lrf sending: {CORE_TO_LRF_MSG}")
    uart_lrf.write(CORE_TO_LRF_MSG)  # Encode the string to bytes

    if uart_core.in_waiting > 0:
        received_data = uart_core.read(uart_lrf.in_waiting)
    else:
        received_data = b''
    print(f"uart_core received: {received_data}")
    print("LRF_TO_CORE:", received_data == CORE_TO_LRF_MSG)
    return received_data == CORE_TO_LRF_MSG


while True:
    led6_red.value = False
    led7_green.value = False

    status = core_to_lrf() and lrf_to_core()

    led6_red.value = not status
    led7_green.value = status

    time.sleep(2)  # Wait for 2 seconds before the next message


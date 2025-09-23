import time

import board
import busio
import digitalio

from lrfemu_min import random_range, request_pack

# defines
# led pins

LED_BOARD_PIN = board.LED

LED_RED_PIN = board.GP21
LED_GREEN_PIN = board.GP22
LED_ACTIVE_HIGH = True

# btn pin
BTN_PIN = board.GP16

LONG_PRESS = 0.7

# uart pins
UART_0_TX_PIN = board.GP4
UART_0_RX_PIN = board.GP5
UART_1_TX_PIN = board.GP12
UART_1_RX_PIN = board.GP13

BAUDRATE_CORE = 115200
BAUDRATE_INF = 115200
BAUDRATE_VEC = 57600

# packet pattern
CORE_TO_VEC_PACKET = b'>Md1\r'
VEC_TO_CORE_PACKET = b'v0222200CE<0D>'

CORE_TO_INF_PACKET = b'\xee\x16\x04\x03\xa1\n\x00\xae'


class UniLED:
    def __init__(self, pin, active_high=True):
        self._pin = digitalio.DigitalInOut(pin)
        self._pin.direction = digitalio.Direction.OUTPUT
        self._active_high = active_high
        self.off()

    @property
    def enabled(self):
        return self._pin.value == self._active_high

    def on(self):
        self._pin.value = self._active_high

    def off(self):
        self._pin.value = not self._active_high


def format_bytes_as_hex(data):
    "Formats a byte string as a human-readable hex string."
    return " ".join([f"{b:02X}" for b in data])


def loopback(uart_a, uart_b, data: bytes, timeout=0.5, strip=False):
    uart_a.write(data)
    time.sleep(timeout)
    if uart_b.in_waiting > 0:
        received_data = uart_b.read(uart_b.in_waiting)
    else:
        received_data = b''
    if strip:
        received_data = received_data.strip().strip(b'\x00')

    return received_data


def core_to_vec(uart_core, uart_lrf):
    "CORE_TO_LRF:"
    print(f"uart_core sending: {format_bytes_as_hex(CORE_TO_VEC_PACKET)}")
    received_data = loopback(uart_core, uart_lrf, CORE_TO_VEC_PACKET)
    state = received_data == CORE_TO_VEC_PACKET
    print(f"uart_lrf received: {format_bytes_as_hex(received_data)}, {state=}\n")
    return state


def vec_to_core(uart_lrf, uart_core):
    "LRF_TO_CORE:"
    print(f"uart_lrf sending:  {format_bytes_as_hex(VEC_TO_CORE_PACKET)}")
    received_data = loopback(uart_lrf, uart_core, VEC_TO_CORE_PACKET)
    state = received_data == VEC_TO_CORE_PACKET
    print(f"uart_core received: {format_bytes_as_hex(received_data)}, {state=}\n")
    return state


def core_to_inf(uart_core, uart_lrf):
    "CORE_TO_LRF:"
    print(f"uart_core sending: {format_bytes_as_hex(CORE_TO_INF_PACKET)}")
    received_data = loopback(uart_core, uart_lrf, CORE_TO_INF_PACKET, strip=True)
    state = received_data == CORE_TO_INF_PACKET
    print(f"uart_lrf received: {format_bytes_as_hex(received_data)}, {state=}\n")
    return state


def inf_to_core(uart_lrf, uart_core):
    "LRF_TO_CORE:"
    _range = random_range()
    expected = str(int(_range // 1)).encode('ansi')
    packet = bytes(request_pack(0x02, status=0, range_=_range))
    print(f"uart_lrf sending:  {format_bytes_as_hex(packet)} ({_range})")
    received_data = loopback(uart_lrf, uart_core, packet, strip=True)
    state = received_data == expected
    print(f"uart_core received: {received_data}, expected: {expected}, {state=}\n")
    return state


def check_vec(uart_core, uart_lrf):
    led_red.off()
    led_green.off()

    time.sleep(0.5)

    status0 = core_to_vec(uart_core, uart_lrf)
    time.sleep(0.1)
    status1 = vec_to_core(uart_lrf, uart_core)
    status = status0 and status1

    led_green.on() if status else led_red.on()


def check_inf(uart_core, uart_lrf):
    led_red.off()
    led_green.off()

    time.sleep(0.5)

    status0 = core_to_inf(uart_core, uart_lrf)
    time.sleep(0.1)
    status1 = inf_to_core(uart_lrf, uart_core)
    status = status0 and status1

    led_green.on() if status else led_red.on()


def wait_button_action(on_press=None, on_long_press=None):
    # Waiting for press
    while btn.value:  # HIGH = not pressed
        time.sleep(0.01)

    t0 = time.monotonic()
    long_triggered = False

    while not btn.value:  # while keep pressing
        if not long_triggered and (time.monotonic() - t0) >= LONG_PRESS:
            long_triggered = True
            print("long press triggered!")
            # Run long press callback
            if on_long_press:
                on_long_press()
        time.sleep(0.01)

    # Button released, returning result
    if long_triggered:
        return 1
    else:
        print("short press")
        if on_press:
            on_press()
        return 0


def switch_mode():
    global check_func
    if led_board.enabled:
        uart_1.baudrate = BAUDRATE_INF
        check_func = check_inf
        led_board.off()
    else:
        uart_1.baudrate = BAUDRATE_VEC
        check_func = check_vec
        led_board.on()
    print("switch mode to", "VEC" if led_board.enabled else "INF")


# init pins
btn = digitalio.DigitalInOut(BTN_PIN)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP

# Pin definitions for pins 6 and 7
# The RP2040 Zero board labels these as GP6 and GP7
led_board = UniLED(LED_BOARD_PIN, True)
led_red = UniLED(LED_RED_PIN, LED_ACTIVE_HIGH)
led_green = UniLED(LED_GREEN_PIN, LED_ACTIVE_HIGH)

uart_0 = busio.UART(UART_0_TX_PIN, UART_0_RX_PIN, baudrate=BAUDRATE_CORE, timeout=1.0)  # CORE
uart_1 = busio.UART(UART_1_TX_PIN, UART_1_RX_PIN, baudrate=BAUDRATE_INF, timeout=1.0)  # LRF (INF)

if __name__ == "__main__":
    print("Starting UART loopback test...")
    led_board.off()
    check_func = check_inf

    while True:
        wait_button_action(
            on_press=lambda: check_func(uart_0, uart_1),
            on_long_press=switch_mode,
        )

        time.sleep(0.1)


# class DongleTester:
#     def __init__(self, uart_core, uart_lrf):
#         self.uart_core = uart_core
#         self.uart_lrf = uart_lrf
#
# class Dongle:
#     def __init__(self, tester: DongleTester):
#             self._tester = tester
#
#     def lrf2core(self):
#         raise NotImplementedError("lrf2core not implemented")
#
#     def core2lrf(self):
#         raise NotImplementedError("core2lrf not implemented")
#
# class DongleVec(Dongle):
#     BAUDRATE_VEC = 57600
#     CORE_TO_VEC_PACKET = b'>Md1\r'
#     VEC_TO_CORE_PACKET = b'v0222200CE<0D>'
#
#     def __init__(self, tester: DongleTester):
#         super().__init__(tester)
#         self._tester.uart_lrf.baudrate = self.BAUDRATE_VEC
#
#     def lrf2core(self):
#         received_data = loopback(self._tester.uart_lrf, self._tester.uart_core, self.VEC_TO_CORE_PACKET)
#         return received_data == self.VEC_TO_CORE_PACKET
#
#     def cor2lrf(self):
#         received_data = loopback(self._tester.uart_core, self._tester.uart_lrf, self.CORE_TO_VEC_PACKET)
#         return received_data == self.CORE_TO_VEC_PACKET
#
#
# class DongleInf(Dongle):
#     BAUDRATE_INF = 115200
#     CORE_TO_INF_PACKET = b'\xee\x16\x04\x03\xa1\n\x00\xae'
#
#     def __init__(self, tester: DongleTester):
#         super().__init__(tester)
#         self._tester.uart_lrf.baudrate = self.BAUDRATE_INF
#
#     def lrf2core(self):
#         _range = random_range()
#         expected = str(int(_range // 1)).encode('ansi')
#         packet = bytes(request_pack(0x02, status=0, range_=_range))
#         received_data = loopback(self._tester.uart_lrf, self._tester.uart_core, packet, strip=True)
#         return received_data == expected
#
#     def cor2lrf(self):
#         received_data = loopback(self._tester.uart_core, self._tester.uart_lrf, self.CORE_TO_INF_PACKET, strip=True)
#         return received_data == self.CORE_TO_INF_PACKET


# def switch_mode(tester):
#
#     global check_func
#     if led_board.enabled:
#         led_board.off()
#         return DongleInf(tester)
#     else:
#         led_board.on()
#         return DongleVec(tester)

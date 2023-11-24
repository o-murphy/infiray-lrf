import _thread

from src.oled import *
from src.parser import *
from src.pinout import *


def on_message(data):
    global ERR_COUNT
    try:
        cmd, resp_data = message_unpack(bytearray(data))

        if cmd in [0x02, 0x04]:
            on_result(f"{resp_data['d']}m")

        elif cmd == 0x06:
            on_result(f"Err:x{resp_data['status']:02X}")
            ERR_COUNT += 1
            on_status(f"{resp_data['mask']} err: {ERR_COUNT}")

        elif cmd == 0x05:
            pass

    except Exception as exc:
        print(exc)
        on_result("Undef")


def set_lrf_frequency(uart):
    uart.write(b'\xee\x16\x04\x03\xa1\n\x00\xae')  # frequency 10
    # uart.write(b'\xee\x16\x04\x03\xa1\x05\x00\xa9')  # frequency 5
    # uart.write(b'\xee\x16\x04\x03\xa1\x02\x00\xa6')  # frequency 2
    # uart.write(b'\xee\x16\x04\x03\xa1\x01\x00\xa5')  # frequency 1
    time.sleep(0.25)


def run(uart):
    b0_prev = button0.value()
    b1_prev = button1.value()
    boot_btn_prev = boot_button.value()

    while True:
        boot_btn_val = button0.value()
        b0_val = button0.value()
        b1_val = not button1.value()

        if boot_btn_prev != boot_btn_val and not boot_btn_val:
            boot_btn_prev = boot_btn_val
            if lrf_en.value() == 0:
                lrf_en.on()
                time.sleep(0.25)
                set_lrf_frequency(uart)
                on_result(f"LRF:ON")
                on_state(">_ stopped")
            else:
                lrf_en.off()
                on_result(f"LRF:OFF")
                on_state(">_ disabled")

        if b0_prev != b0_val and b0_val:
            b0_prev = b0_val

            on_state(">_ ranging")

            uart.write(message_pack(0x02))

            for i in range(len(range_spinner.states)):
                spin(range_spinner)
                time.sleep(0.1)

            spin(range_spinner, -1)
            on_state(">_ stopped")

        if b1_prev != b1_val:
            b1_prev = b1_val

            if not b1_val:
                uart.write(message_pack(0x04))
                on_state(">_ scanning")
            else:
                uart.write(message_pack(0x05))
                on_state(">_ stopped")
                spin(scan_spinner, -1)

        if not b1_val:
            spin(scan_spinner)

        time.sleep(0.02)


show_hello()

# init globalvars
ERR_COUNT = 0
scan_spinner = Spinner()
range_spinner = Spinner(states=["===", ">=<", "=x=", ])

# init gui
init_gui()
spin(range_spinner, -1)
on_state(">_ stopped ")

# start uart read thread
_thread.start_new_thread(read_uart, (uart, on_message))

# init_lrf
lrf_en.on()
set_lrf_frequency(uart)

# run main thread loop
run(uart)

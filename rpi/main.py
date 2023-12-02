try:
    from machine import UART, ADC, Pin
    from parser import response_unpack
except ImportError as err:
    print("fake machine")
    from rpi.fake_machine import UART, ADC, Pin
    from rpi.parser import response_unpack

import time
import _thread


uart_dev = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
uart_lrf = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))


led = Pin('LED', Pin.OUT)
led.on()

pot = ADC(Pin(26))

prev_pot = 0
time_init = time.time()

ctr = 0
def log(msg):
    global ctr
    print(ctr)
    ctr += 1
    with open('log.txt', 'a') as fp:
        fp.write(f"{run_time()}\t{msg}\n")


def read_uart_dev():
    while True:

        try:
            upd_acp_value()
            data = uart_dev.read(1)

            if data == b'\xee':
                time.sleep(0.01)
                data += uart_dev.read(2)
                if data:
                    expected_length = data[2] + 1
                    data += uart_dev.read(expected_length)
                    log(f"dev > dongle {data}")
                    uart_lrf.write(data)
                    log(f"dongle > lr {data}")

            elif data == b'' or not data:
                pass
            else:
                pass

            time.sleep(0.02)
        except Exception as err:
            # print(err)
            led.off()
            time.sleep(1)
            led.on()


def read_uart_lrf():
    while True:
        try:

            data = uart_lrf.read(1)

            if data == b'\xee':
                time.sleep(0.02)
                data += uart_lrf.read(2)
                if data:
                    expected_length = data[2] + 1
                    data += uart_lrf.read(expected_length)
                    log(f"lr > dongle {data}")

                    cmd, result = response_unpack(data)
                    if cmd in (0x02, 0x04) and result['s'] != 0x06:
                        _out = (str(result['r']) + '\n').encode('ascii')
                        uart_dev.write(_out)
                        log(f"dongle > dev {_out}")

            elif data == b'' or not data:
                pass
            else:
                pass

            time.sleep(0.02)
        except Exception as err:
            # print(err)
            led.off()
            time.sleep(0.5)
            led.on()
            time.sleep(0.5)
            led.off()
            time.sleep(0.5)
            led.on()


def acp_value():
    pot_value = pot.read_u16()
    return (pot_value * 3.3) / 65535


def upd_acp_value():
    global prev_pot
    pot_value = acp_value()
    if pot_value - prev_pot >= 0.01:
        # print(f"{run_time()} {pot_value}")
        log(f" lr5v {pot_value}")
        prev_pot = pot_value


def run_time():
    return int((time.time() - time_init) * 100)


_thread.start_new_thread(read_uart_lrf, ())

# while True:
#    time.sleep(1)
read_uart_dev()


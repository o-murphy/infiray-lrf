"""
Command sender for the InfiRay LR2000 / LR3000 Long Range Finder
(C) 2023 Yaroshenko Dmytro (https://github.com/o-murphy)
"""

import sys
import threading
import time

# Function to read data from the serial port
import serial
from construct import ChecksumError
from serial.tools.list_ports import comports

from infiray_lrf.commands import COMMAND, command_request_struct, command_response_struct
from infiray_lrf.logger import logger


def parse_lrf_resp(counter, data):
    try:
        resp = command_response_struct.parse(data)

        if resp.cmd in (COMMAND.SingleRanging, COMMAND.ContinuousRanging):
            logger.info(f' LRF resp {counter}, {resp.cmd}: {resp.params.range}m')

        elif resp.cmd == COMMAND.RangingAbnormal:
            logger.info(f' LRF resp {counter}, {resp.cmd}: {resp.params}')

        elif resp.cmd == COMMAND.StopRanging:
            logger.info(f' LRF resp {counter}, {resp.cmd}')

        elif resp.cmd == COMMAND.SetFrequency:
            logger.info(f' LRF resp {counter}, {resp.cmd}')

        else:
            print(resp)

    except ChecksumError:
        logger.info(f' LRF {counter}, CRC ERR: {data}')
        raise ValueError
    except Exception as exc:
        logger.error(exc)


def read_serial(intf):
    logger.info(f" Trying to connect port {intf.port}")
    logger.info(f" {intf.port} opened")
    if intf.is_open:
        try:

            logger.info(f" RESP {intf.port} opened")
            counter = 0
            while not EXIT:
                data = intf.read(1)
                if data == b'\xee':
                    len_eq = bytearray(intf.read(2))
                    expected_length = len_eq[1] + 1
                    data += len_eq
                    data += intf.read(expected_length)

                    counter += 1
                    parse_lrf_resp(counter, data)
                elif data == b'':
                    pass
                else:
                    logger.info(f' RESP: {data}')

        except Exception as exc:
            intf.close()
            logger.error(exc)


# Function to write data to the serial port
def write_serial(intf):
    while True:
        if intf.is_open:
            try:

                # Get user input and write it to the serial port
                message = input('Enter message to send: \n')

                cmd = None

                if message == 's':
                    cmd = command_request_struct.build({'cmd': COMMAND.SingleRanging, 'params': None})

                elif message == 'i':
                    cmd = command_request_struct.build({'cmd': COMMAND.SelfInspection, 'params': None})

                elif message == 'C':
                    cmd = command_request_struct.build({'cmd': COMMAND.ContinuousRanging, 'params': None})

                elif message.startswith('cf'):
                    _, freq, timeout = message.split()
                    cmd = command_request_struct.build(
                        {'cmd': COMMAND.SetFrequency, 'params': {'freq': int(freq)}})
                    intf.write(cmd)
                    time.sleep(0.25)
                    cmd = command_request_struct.build({'cmd': COMMAND.ContinuousRanging, 'params': None})
                    intf.write(cmd)
                    time.sleep(int(timeout))
                    cmd = command_request_struct.build({'cmd': COMMAND.StopRanging, 'params': None})
                    intf.write(cmd)
                    cmd = None

                elif message == 'b':
                    cmd = command_request_struct.build({'cmd': COMMAND.StopRanging, 'params': None})

                elif message.startswith('freq'):
                    _, freq = message.split()
                    if not (1 <= int(freq) <= 10):
                        raise ValueError(f'freq: 1-10 expected, got {freq}')
                    cmd = command_request_struct.build(
                        {'cmd': COMMAND.SetFrequency, 'params': {'freq': int(freq)}})

                elif message == 'glg':
                    cmd = command_request_struct.build({'cmd': COMMAND.GetMinGate, 'params': None})

                elif message.startswith('slg'):
                    _, val = message.split()
                    if not (10 <= int(val) <= 20000):
                        raise ValueError(f'slg: 10-20000 expected, got {val}')
                    cmd = command_request_struct.build({'cmd': COMMAND.SetMinGate, 'params': int(val)})

                elif message == 'ghg':
                    cmd = command_request_struct.build({'cmd': COMMAND.GetMaxGate, 'params': None})

                elif message.startswith('shg'):
                    _, val = message.split()
                    if not (10 <= int(val) <= 20000):
                        raise ValueError(f'shg: 10-20000 expected, got {val}')
                    cmd = command_request_struct.build({'cmd': COMMAND.SetMaxGate, 'params': int(val)})

                elif message == 'fpga':
                    cmd = command_request_struct.build({'cmd': COMMAND.FpgaVer, 'params': None})

                elif message == 'mcu':
                    cmd = command_request_struct.build({'cmd': COMMAND.McuVer, 'params': None})

                elif message == 'hw':
                    cmd = command_request_struct.build({'cmd': COMMAND.HWVer, 'params': None})

                elif message == 'sn':
                    cmd = command_request_struct.build({'cmd': COMMAND.SN, 'params': None})

                elif message == 'total':
                    cmd = command_request_struct.build({'cmd': COMMAND.TotalCount, 'params': None})

                elif message == 'count':
                    cmd = command_request_struct.build({'cmd': COMMAND.PowerCount, 'params': None})

                elif message == 'h':
                    show_help()

                elif message == 'q':
                    return

                elif message.startswith('setbaudrate'):
                    _, baudrate = message.split()
                    if int(baudrate) not in (115200, 57600, 9600):
                        raise ValueError(f'baudrate: 115200/57600/9600 expected, got {baudrate}')
                    cmd = command_request_struct.build(
                        {'cmd': COMMAND.SetBaudRate, 'params': int(baudrate)})

                if cmd:
                    try:
                        cmd_name = command_request_struct.parse(cmd).cmd
                        logger.info(f' REQ: {cmd_name}')
                    except Exception:
                        logger.info(f' REQ: {cmd}')
                    intf.write(cmd)

            except serial.SerialException as e:
                logger.error(f' Error writing to serial port: {e}')
            except ValueError as err:
                logger.error(f" Wrong command: {err}")


EXIT = False


def show_help():
    print("""
Commands list:

q\t - quit
h\t - help

i\t - self inspection

s\t - single ranging
cf <int:frequency> <int:timeout> 
\t - continious ranging (frequency 1~10Hz, timout - seconds)
C\t - nonstop continious ranging
b\t - stop ranging
freq <int:frequency>
\t - set continious ranging frequency (1~10Hz)
\t 
glg\t - query minimum gating distance
ghg\t - query maximum gating distance
slg <int:distance>
\t - set minimum gating distance (10-20000m)
shg <int:distance>
\t - set maximum gating distance (10-20000m)

fpga\t - query FPGA software version number
mcu\t - query MCU software version number
hw\t - query hardware version number
sn\t - query SN number

total\t - count of times of light resput
count\t - count of times of light resput since LRF power up

setbaudrate <int:baudrate>
\t\t - set baudrate value (115200 / 57600 / 9600)\n\n
""")


def main():
    global EXIT
    print("Available ports:\n" + ', '.join([p.name for p in comports()]) + '\n')

    # lrf in
    port_index = input("LRF req port number: ")

    # Configure the serial port
    intf = serial.Serial(f'COM{port_index}', 115200, timeout=1)
    show_help()

    # Create threads for reading and writing
    read_thread = threading.Thread(target=read_serial, args=(intf,), daemon=True)
    write_thread = threading.Thread(target=write_serial, args=(intf,), daemon=True)

    # Start the threads
    read_thread.start()
    write_thread.start()

    write_thread.join()
    EXIT = True
    intf.close()
    sys.exit(0)


if __name__ == '__main__':
    main()

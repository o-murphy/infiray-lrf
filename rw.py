import logging
import time

import serial
from serial.tools.list_ports import comports

import threading


# Function to read data from the serial port
from main import *


# print(ranging.parse(b'\xee\x16\x02\x03\x04\x08'))
#
# print(ranging.build(dict(cmd=ranging_cmd.stop)))


def read_serial(intf):
    logging.info(f" Trying to connect port {intf.port}")
    logging.info(f" {intf.port} opened")
    if intf.is_open:
        try:

            logging.info(f" RESP {intf.port} opened")
            counter = 0
            while True:
                data = intf.read(1)
                if data == b'\xee':
                    data += intf.read(9)
                    counter += 1
                    parse_lrf_resp(counter, data)
                elif data == b'':
                    pass
                else:
                    logging.info(f' RESP: {data}')

        except Exception as exc:
            intf.close()
            logging.error(exc)


# Function to write data to the serial port
def write_serial(intf):
    while True:
        if intf.is_open:
            try:
                # Get user input and write it to the serial port
                message = input('Enter message to send: \n')
                cmd = None
                if message == 's':
                    cmd = ranging.build({'cmd': ranging_cmd.single})

                if message == 'c':
                    cmd = ranging.build({'cmd': ranging_cmd.continuous})

                if message == 'b':
                    cmd = ranging.build({'cmd': ranging_cmd.stop})
                if cmd:
                    intf.write(cmd)
                    logging.info(f' REQ: {cmd}')
            except serial.SerialException as e:
                logging.error(f' Error writing to serial port: {e}')


def main():
    print("Available ports:\n" + ', '.join([p.name for p in comports()]) + '\n')

    # lrf in
    port_index = input("LRF req port number: ")

    # Configure the serial port
    intf = serial.Serial(f'COM{port_index}', 115200, timeout=1)

    # Create threads for reading and writing
    read_thread = threading.Thread(target=read_serial, args=(intf,), daemon=True)
    write_thread = threading.Thread(target=write_serial, args=(intf,), daemon=True)

    # Start the threads
    read_thread.start()
    write_thread.start()

    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Close the serial port when the program is interrupted
        intf.close()


if __name__ == '__main__':
    main()
import logging
import serial
from serial.tools.list_ports import comports


logging.basicConfig(level=logging.INFO, format="%(asctime)s;%(levelname)s;%(message)s")


def read(index):
    intf = serial.Serial()
    intf.baudrate = 115200
    intf.port = f'COM{index}'
    logging.info(f"Trying to connect port {intf.port}")
    counter = 0
    try:
        buf = b''
        intf.open()
        if intf.is_open:
            logging.info(f"{intf.port} opened")
            while True:
                data = intf.read(1)
                if data == b'\n':
                    counter += 1
                    logging.info(f"{counter}, {buf}")
                    buf = b''
                else:
                    buf += data

    except Exception as exc:
        intf.close()
        logging.error(exc)


if __name__ == '__main__':
    while True:
        print("Available ports:\n" + ', '.join([p.name for p in comports()]) + '\n')
        port_index = input("Port number: ")
        read(port_index)
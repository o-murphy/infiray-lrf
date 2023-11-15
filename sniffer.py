import logging
from time import sleep

import serial
from commands import *
from construct import ChecksumError
from serial.tools.list_ports import comports
from threading import Thread

formatter = logging.Formatter(
    "%(asctime)s;%(levelname)s;%(message)s",
    datefmt="%H:%M:%S"
)
chanel = logging.StreamHandler()
chanel.setFormatter(formatter)
logger = logging.getLogger("root")
logger.setLevel(logging.INFO)
logger.addHandler(chanel)


# test_data = b'\xee\x16\x06\x03\x02\x00\x00\x0c\x04\x15'
# print(recieve.parse(test_data))


def parse_lrf_resp(counter, data):
    try:

        resp = ranging_response.parse(data)
        if resp.command == 0x2:
            logging.info(f' LRF resp {counter}, SING: {resp.range}m')
        elif resp.command == 0x4:
            logging.info(f' LRF resp {counter}, CONT: {resp.range}m')
        else:
            logging.info(f' LRF resp {counter}, {int(resp.command)}: {resp.range}m')
    except ChecksumError:
        logging.info(f' LRF {counter}, CRC ERR: {data}')
    except Exception as exc:
        logging.error(exc)


def read_lrf_resp(index):
    intf = serial.Serial()
    intf.baudrate = 115200
    intf.port = f'COM{index}'
    logging.info(f"Trying to connect port {intf.port}")
    try:
        intf.open()
        if intf.is_open:
            logging.info(f" LRF resp {intf.port} opened")
            counter = 0
            while True:
                data = intf.read(1)
                if data == b'\xee':
                    data += intf.read(9)
                    counter += 1
                    parse_lrf_resp(counter, data)
                else:
                    logging.info(f' LRF resp Trash: {data}')

    except Exception as exc:
        intf.close()
        logging.error(exc)
        
        
def read_lrf_req(index):
    intf = serial.Serial()
    intf.baudrate = 115200
    intf.port = f'COM{index}'
    logging.info(f"Trying to connect port {intf.port}")
    try:
        intf.open()
        if intf.is_open:
            logging.info(f" LRF req {intf.port} opened")
            counter = 0
            while True:
                data = intf.read(1)
                if data == b'\xee':
                    data += intf.read(5)
                    counter += 1
                    try:
                        req = ranging_cmd.parse(data)
                        logging.info(f' LRF req {counter}, {req.cmd}')
                    except Exception:
                        logging.info(f' LRF req {counter}, {data}')

                else:
                    logging.info(f' LRF req Trash: {data}')

    except Exception as exc:
        intf.close()
        logging.error(exc)


def read_stm_req(index):
    intf = serial.Serial()
    intf.baudrate = 115200
    intf.port = f'COM{index}'
    logging.info(f"Trying to connect port {intf.port}")
    try:
        intf.open()
        if intf.is_open:
            logging.info(f" STM req {intf.port} opened")
            counter = 0
            while True:
                data = intf.read(1)
                if data == b'\xee':
                    data += intf.read(5)
                    counter += 1
                    try:
                        req = ranging_cmd.parse(data)
                        logging.info(f' LRF req {counter}, {req.cmd}')
                    except Exception:
                        logging.info(f' LRF req {counter}, {data}')

                else:
                    logging.info(f' STM req Trash: {data}')

    except Exception as exc:
        intf.close()
        logging.error(exc)


def read_stm_resp(index):
    intf = serial.Serial()
    intf.baudrate = 115200
    intf.port = f'COM{index}'
    logging.info(f"Trying to connect port {intf.port}")
    counter = 0
    try:
        buf = b''
        intf.open()
        if intf.is_open:
            logging.info(f" STM resp {intf.port} opened")
            while True:
                data = intf.read(1)
                if data == b'\n':
                    counter += 1
                    logging.info(f" STM resp {counter}, {buf}")
                    buf = b''
                else:
                    buf += data

    except Exception as exc:
        intf.close()
        logging.error(exc)


def read_anything(intf):
    logging.info(f"Trying to connect port {intf.port}")
    try:
        if intf.is_open:
            logging.info(f" {intf.port} opened")
            while True:
                data = intf.read(1)
                logging.info(f" {intf.port} {data}")
                sleep(0.25)

    except Exception as exc:
        intf.close()
        logging.error(exc)


def main():
    print("Available ports:\n" + ', '.join([p.name for p in comports()]) + '\n')

    threads = []

    # lrf in
    if int(port_index := input("LRF req port number: ")) > 0:
        threads.append(Thread(target=lambda idx=port_index: read_lrf_req(idx)))

    # stm in
    if int(port_index := input("Stm req port number: ")) > 0:
        threads.append(Thread(target=lambda idx=port_index: read_stm_req(idx)))

    # lrf resp
    if int(port_index := input("LRF resp port number: ")) > 0:
        threads.append(Thread(target=lambda idx=port_index: read_lrf_resp(idx)))

    # stm resp
    if int(port_index := input("Stm resp port number: ")) > 0:
        threads.append(Thread(target=lambda idx=port_index: read_stm_resp(idx)))

    for t in threads:
        t.start()


"""
26 - lrf req
40 - lrf resp

"""


if __name__ == '__main__':
    main()

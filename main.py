import logging

import serial
from construct import Struct, Byte, Const, Checksum, ChecksumError, Enum, Bytes, Int8sb, Int16sb, Computed
from serial.tools.list_ports import comports

logging.basicConfig(level=logging.INFO, format="%(asctime)s;%(levelname)s;%(message)s")
# test_data = b'\xee\x16\x06\x03\x02\x00\x00\x0c\x04\x15'
# print(recieve.parse(test_data))


def crc(ctx):
    if ctx._parsing:
        data = ctx._io.getvalue()
        return sum(data[3:-1]) & 0xFF
    return 0xFF


command = Enum(
    Byte,
    SelfInspection=0x01,
    SingleRanging=0x02,
    SetFirstLast=0x03,  # "Set first / last / multiple targets "
    ContinuousRranging=0x04,
    StopRanging=0x05,
    SetBaudRate=0xa0,
    SetFrequency=0xa1,  # "Set continuous ranging frequency",
    SetMinGate=0xa2,  # "Set minimum gating distance",
    GetMinGate=0xa3,  # "Query minimum gating distance",
    MaxGate=0xa4,  # "Maximum gating distance",
    GetMaxGate=0xa5,  # "Query the maximum gating distance",
    FpgaVer=0xa6,  # "Query FPGA software version number",
    McuVer=0xa7,  # "Query MCU software version number",
    HWVer=0xa8,  # "Query hardware version number",
    SN=0xa9,  # "Query Sn number",
    Counter=0x90,  # "Total times of light output ",
    PowerLight=0x91,  # "Query the power on and light out times this time"
)


response = Struct(
    'header' / Const(b'\xee\x16'),
    'length' / Byte,
    'equip' / Const(0x3, Byte),
    'command' / command,
    'status' / Byte,
    '_range' / Int16sb,
    '_dec' / Int8sb,
    'range' / Computed(lambda ctx: ctx._range + ctx._dec / 10),
    'crc' / Checksum(Byte, crc, lambda ctx: ctx)
)


def read_valid(index):
    intf = serial.Serial()
    intf.baudrate = 115200
    intf.port = f'COM{index}'
    logging.info(f"Trying to connect port {intf.port}")
    try:
        intf.open()
        if intf.is_open:
            logging.info(f"{intf.port} opened")
            counter = 0
            while True:
                data = intf.read(1)
                if data == b'\xee':
                    data += intf.read(9)
                    counter += 1
                    try:
                        print(response.parse(data))
                        logging.info(f'{counter}, Valid: {data}')
                    except ChecksumError:
                        logging.info(f'{counter}, CRC ERR: {data}')
                else:
                    logging.info(f'Trash: {data}')

    except Exception as exc:
        intf.close()
        logging.error(exc)


if __name__ == '__main__':
    while True:
        print("Available ports:\n" + ', '.join([p.name for p in comports()]) + '\n')
        port_index = input("Port number: ")
        read_valid(port_index)

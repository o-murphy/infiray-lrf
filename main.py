import logging
import serial
from serial.tools.list_ports import comports
from construct import *


logging.basicConfig(level=logging.INFO)
# test_data = b'\xee\x16\x06\x03\x02\x00\x00\x0c\x04\x15'
# print(recieve.parse(test_data))


command = Enum(
    Byte,
    SelfInspection=0x01,
    SingleRanging=0x02,
    SetFirstLast=0x03,  # "Set first / last / multiple targets "
    ContinuousRranging = 0x04,
    StopRanging = 0x05,
    SetBaudRate = 0xa0,
    SetFrequency = 0xa1,  # "Set continuous ranging frequency",
    SetMinGate = 0xa2,  # "Set minimum gating distance",
    GetMinGate = 0xa3,  # "Query minimum gating distance",
    MaxGate = 0xa4,  # "Maximum gating distance",
    GetMaxGate = 0xa5,  # "Query the maximum gating distance",
    FpgaVer = 0xa6,  # "Query FPGA software version number",
    McuVer = 0xa7,  # "Query MCU software version number",
    HWVer = 0xa8,  # "Query hardware version number",
    SN = 0xa9,  # "Query Sn number",
    Counter = 0x90,  # "Total times of light output ",
    PowerLight = 0x91,  # "Query the power on and light out times this time"
)


def crc(ctx):
    if ctx._parsing:
        data = ctx._io.getvalue()
        return sum(data[3:-1]) & 0xFF
    return 0xFF


recieve = Struct(
    'header' / Bytes(2),
    'length' / Byte,
    'equip' / Byte,
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
            while True:
                data = intf.read(1)
                if data == b'\xee':
                    data += intf.read(9)
                    print("Valid: ", data)
                    try:
                        print(recieve.parse(data))
                        print("Valid: ", data)
                    except ChecksumError:
                        print("CRC ERR: ", data)
                else:
                    print("Trash: ", data)

    except Exception as exc:
        intf.close()
        logging.error(exc)


if __name__ == '__main__':
    while True:
        print("Available ports:\n" + ', '.join([p.name for p in comports()]) + '\n')
        port_index = input("Port number: ")
        read_valid(port_index)

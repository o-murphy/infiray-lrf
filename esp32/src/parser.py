import struct
import time


CMD_STR = {
    0x01: 'Self Inspection',
    0x02: 'Single Ranging',
    0x04: 'Scanning',
    0x05: 'Stop Scanning',
    0x06: 'Ranging Error',
}


def crc(data):
    return sum(data[3:-1]) & 0xFF


def check_crc(data):
    return crc(data) == data[-1]


def range_resp_unpack(data):
    s, r, d = struct.unpack(">BhB", data)
    return dict(s=s, d=f'{r}.{d}')


def range_abnormal_unpack(data):
    status, *_ = struct.unpack(">xxxB", data)
    # t, bo, bs, ec, w, lo, fp, *r = [
    #     '-' if i == '1' else 'x' for i in "{:08b}".format(status)
    # ]
    mask = ['-' if i == '1' else 'x' for i in "{:08b}".format(status)]
    return dict(mask=''.join(mask[:7]), status=status)


def range_resp_pack(status, range: float):
    r, d = int(range // 1), int(range % 1 * 10)
    return struct.pack(">BhB", status, r, d)


def continuous_resp_pack(status, range: float):
    r, d = int(range // 1), int(range % 1 * 10)
    return struct.pack(">BhB", status, r, d)


def range_abnormal_pack(*args, **kwargs):
    return b''


def set_frequency_pack(value):
    print(struct.pack("<h", value))
    return struct.pack("<h", value)


def set_lrf_frequency(uart, value):
    uart.write(message_pack(0xa1, value=value))
    time.sleep(0.25)


MessageBuilder = {
    0x02: lambda: b'',
    0x04: lambda: b'',
    0x05: lambda: b'',
    0xa1: set_frequency_pack
}


MessageParser = {
    0x02: range_resp_unpack,
    0x04: range_resp_unpack,
    0x05: lambda *args, **kwargs: {},
    0x06: range_abnormal_unpack,
    0xa1: lambda *args, **kwargs: {}  # TODO
}


def message_unpack(data):
    hh, hl, ln, q, cmd = struct.unpack('<BBBBB', data[:5])
    if not check_crc(data):
        raise ValueError("Wrong CRC")
    if not cmd in MessageParser:
        raise ValueError("Wrong CMD")
    func = MessageParser[cmd]
    return cmd, func(data[5:-1])


def message_pack(cmd, **kwargs):
    data = bytearray(b'\xee\x16\xff\x03')
    data.append(cmd)

    if not cmd in MessageBuilder:
        raise ValueError("Wrong CMD")
    func = MessageBuilder[cmd]
    data.extend(func(**kwargs))
    data.append(0xff)
    data[2] = len(data) - 4
    data[-1] = crc(data)
    return data


def read_uart(uart, on_message=None):
    print('uart', on_message)
    data = uart.read(1)
    if data == b'\xee':
        time.sleep(0.01)
        _d = uart.read(2)
        if _d:
            len_eq = bytearray(_d)
            expected_length = len_eq[1] + 1
            data += len_eq
            data += uart.read(expected_length)

            # if callable(on_message):
            on_message(data)
    time.sleep(0.02)

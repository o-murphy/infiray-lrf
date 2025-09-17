import struct
import time
import random


CMD_STR = {
    0x01: 'Self Inspection',
    0x02: 'Single Ranging',
    0x04: 'Scanning',
    0x05: 'Stop Scanning',
    0x06: 'Ranging Error',
}

FMT = {
    0x01: '> Insp:',
    0x02: '> Range: {d}m\nStatus: {s}',
    0x04: '> Range: {d}m\nStatus: {s}',
    0x05: '> Stopped',
    0x06: '> Ranging Error\nf{fp} l{lo} w{w} e{ec}\nt{t} bs{bs} bo{bo}',
}


def crc(data):
    return sum(data[3:-1]) & 0xFF


def range_resp_pack(status, range: float):
    r, d = int(range // 1), int(range % 1 * 10)
    return struct.pack(">BhB", status, r, d)


def continuous_resp_pack(status, range: float):
    r, d = int(range // 1), int(range % 1 * 10)
    return struct.pack(">BhB", status, r, d)


def range_abnormal_pack(*args, **kwargs):
    return b''


RequestBuilder = {
    0x02: range_resp_pack,
    0x04: continuous_resp_pack,
    0x05: lambda *args, **kwargs: {},
    0x06: range_abnormal_pack,
}

ResponseParser = {
    0x02: lambda *args: {},
    0x04: lambda *args: {},
    0x05: lambda *args: {},
}


def check_crc(data):
    return crc(data) == data[-1]

def response_unpack(data):
    hh, hl, ln, q, cmd = struct.unpack('<BBBBB', data[:5])
    if not check_crc(data):
        raise ValueError("Wrong CRC")
    if not cmd in ResponseParser:
        raise ValueError("Wrong CMD")
    func = ResponseParser[cmd]
    return cmd, func(data[5:-1])


def request_pack(cmd, **kwargs):
    data = bytearray(b'\xee\x16\xff\x03')
    data.append(cmd)

    if not cmd in RequestBuilder:
        raise ValueError("Wrong CMD")
    func = RequestBuilder[cmd]
    data.extend(func(**kwargs))
    data.append(0xff)
    data[2] = len(data) - 4
    data[-1] = crc(data)
    return data

def random_range():
    return random.randrange(0, 30000, 1) / 10


if __name__ == "__main__":
    c = 0
    while 1:
        print(c)
        c += 1
        _range = 19.0
        d = request_pack(0x02, status=0, range=_range)
        print(d)

        time.sleep(0.2)


import struct
from random import randrange


def crc(data):
    return sum(data[3:-1]) & 0xFF


def range_resp_pack(status, range_: float):
    r, d = int(range_ // 1), int(range_ % 1 * 10)
    return struct.pack(">BhB", status, r, d)


RequestBuilder = {0x02: range_resp_pack}


def request_pack(cmd, **kwargs):
    data = bytearray(b'\xee\x16\xff\x03')
    data.append(cmd)

    if not cmd in RequestBuilder:
        raise ValueError("Wrong CMD")
    data.extend(range_resp_pack(**kwargs))
    data.append(0xff)
    data[2] = len(data) - 4
    data[-1] = crc(data)
    return data


def random_range():
    return randrange(1000, 20000, 1) / 10


if __name__ == "__main__":
    import time

    c = 0
    while 1:
        print(c)
        c += 1
        _range = random_range()
        packet = request_pack(0x02, status=0, range_=_range)
        print(packet)

        time.sleep(0.2)

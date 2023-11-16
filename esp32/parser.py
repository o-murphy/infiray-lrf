import struct

from infiray_lrf.commands import command_response_struct

CMD_STR = {
    0x01: 'SelfInspection',
    0x02: 'SingleRanging',
    0x03: 'SetFirstLast',
    0x04: 'ContinuousRanging',
    0x05: 'StopRanging',
    0x06: 'RangingAbnormal',
}

STR_CMD = {
    'SelfInspection': 0x01,
    'SingleRanging': 0x02,
    'SetFirstLast': 0x03,
    'ContinuousRanging': 0x04,
    'StopRanging': 0x05,
    'RangingAbnormal': 0x06,
}


def crc(data):
    return sum(data[3:-1]) & 0xFF


def range_resp_unpack(data):
    s, r, d = struct.unpack(">bHb", data)
    return dict(s=s, d=f'{r}.{d}')


def range_abnormal_unpack(data):
    status, *_ = struct.unpack(">xxxb", data)
    t, bo, bs, ec, w, lo, fp, *r = "{:08b}".format(status)
    return dict(t=t, bo=bo, bs=bs, ec=ec, w=w, lo=lo, fp=fp)


RequestBuilder = {
    0x02: lambda: b'',
    0x04: lambda: b'',
}

ResponseParser = {
    0x02: range_resp_unpack,
    0x04: range_resp_unpack,
    0x06: range_abnormal_unpack,
}


# THeader = b'\xee\x16\x03\x02\x01'
FHeader = '<cccbb'


def check_crc(data):
    return crc(data) == data[-1]


def response_unpack(data):

    hh, hl, ln, q, cmd = struct.unpack(FHeader, data[:5])
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


# data = bytearray(b'\xee\x16\x06\x03\x06\x00\x00\x00\x07\x19')
# data[-1] = crc(data)
#
# print(command_response_struct.parse(
#     data
# ))
# print(data[5:-1])
# response_unpack(
#     data
# )

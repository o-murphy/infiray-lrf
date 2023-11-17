import struct

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


def range_resp_unpack(data):
    s, r, d = struct.unpack(">BhB", data)
    return dict(s=s, d=f'{r}.{d}')


def range_abnormal_unpack(data):
    status, *_ = struct.unpack(">xxxB", data)
    # t, bo, bs, ec, w, lo, fp, *r = [
    #     '-' if i == '1' else 'x' for i in "{:08b}".format(status)
    # ]
    mask = [
        '-' if i == '1' else 'x' for i in "{:08b}".format(status)
    ]
    # return dict(t=t, bo=bo, bs=bs, ec=ec, w=w, lo=lo, fp=fp, status=status)
    return dict(mask=''.join(mask[:7]), status=status)


RequestBuilder = {
    0x02: lambda: b'',
    0x04: lambda: b'',
    0x05: lambda: b'',
    # 0x01: lambda: b'',  # TODO:
}

ResponseParser = {
    0x02: range_resp_unpack,
    0x04: range_resp_unpack,
    0x05: lambda *args: {},
    0x06: range_abnormal_unpack,

    0xa1: lambda *args: {}  # TODO
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

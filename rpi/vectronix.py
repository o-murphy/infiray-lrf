import enum
import random
import time

RANGING_RESPONSE_LEN = 11
ACK = b'>'  # 0x3E
NACK = b'!'  # 0x21
END = b'\r'  # 0x0D
COMMA = b","  # 0x2c


class Command(enum.Enum):
    GET_RANGE = b"Md1"
    SW_HW_INFO = b"Iv1"
    SELF_TEST = b"Tb1"
    LPCL_MODE = b"Tl1"


class RangingStatus(enum.Enum):
    VALID = b'v'
    ERROR = b'R'
    UNKNOWN = 0


class LPCLMode(enum.IntEnum):
    DEACTIVATE = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6


class VectronixRangeFinder:
    def __init__(self, read, write):
        self._read = read
        self._write = write

    def send_command(self, command: Command, lpcl_mode: LPCLMode = None):
        opcode = COMMA + str(lpcl_mode).encode('ascii') if lpcl_mode else b""
        buffer = ACK + command.value + opcode + END
        self._write(buffer)

    def read_response(self):
        while True:
            response = self._read(1)
            if response == END:
                continue
            if response == NACK:
                raise ValueError("Invalid command")
            if response == ACK:
                response += self._read(RANGING_RESPONSE_LEN - 1)
                if len(response) != 11 or response[-1] != 0x0D:  # Validate response length and <CR> at the end
                    raise ValueError("Invalid response format")

            return response

    @staticmethod
    def parse_range(response: bytes):
        status, measured_range, checksum = response[0:1], response[1:8], response[8:10]

        VectronixRangeFinder.check_crc(response)

        response = {
            'range': None,
            'status': None,
            'error': None,
        }

        if status == RangingStatus.VALID:
            response = {
                'range': int(measured_range.decode('ascii')) / 100,
                'status': RangingStatus.VALID,
                'error': None,
            }
        else:
            response = {
                'range': None,
                'status': status == RangingStatus.ERROR or RangingStatus.UNKNOWN,
                'error': response[4:8],
            }

        return response

    @staticmethod
    def check_crc(response: bytes):
        # Extract the data and CRC from the response
        data = response[:8]
        crc_received = response[-3:-1].decode('utf-8')  # Decode received CRC

        # Calculate the CRC from the data
        crc_calculated = f"{sum(data) & 0xFF:02X}"  # Convert to 2-character hex
        # return crc_calculated == crc_received
        if not crc_received == crc_calculated:
            raise ValueError("Invalid CRC")


def range(distance: float = 1087.50) -> bytes:
    formatted_range = f"{int(distance * 100):07d}"  # Pad with zeros to make it 7 digits
    encoded_range = b'v' + formatted_range.encode('ascii').upper()
    crc = sum(encoded_range[:8]) & 0xFF
    encoded_crc = f"{crc:02X}".encode('ascii')
    return encoded_range + encoded_crc + b'\r'


def error():
    return b"R000E301BB"


if __name__ == "__main__":
    # import serial
    #
    # uart = serial.Serial("COM4", timeout=0.1, baudrate=57600)
    # start = time.time()
    # # lrf = VectronixRangeFinder(uart.read, uart.write)
    #
    # try:
    #     while True:
    #         payload = uart.readall()
    #         if Command.GET_RANGE.value in payload:
    #             dst = random.randint(0, 3000)
    #             msg = range(random.randint(0, 3000))
    #             uart.write(msg * 3)
    #
    # except Exception as e:
    #     pass
    # finally:
    #     uart.close()


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


    def range_resp_unpack(data):
        s, r, d = struct.unpack(">BhB", data)
        return dict(s=s, d=float(f'{r}.{d}'), r=r)


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

    ResponseParser = {
        0x02: range_resp_unpack,
        0x04: range_resp_unpack,
        0x05: lambda *args: {},
        0x06: range_abnormal_unpack,

        0xa1: lambda *args: {}  # TODO
    }

    # def response_unpack(data):
    #     hh, hl, ln, q, cmd = struct.unpack('<BBBBB', data[:5])
    #     if not check_crc(data):
    #         raise ValueError("Wrong CRC")
    #     if not cmd in ResponseParser:
    #         raise ValueError("Wrong CMD")
    #     func = ResponseParser[cmd]
    #     return cmd, func(data[5:-1])

    _range = random.randint(0, 3000)
    print(_range)
    range_response = request_pack(0x02, status=0, range=_range)
    print(range_response)

    # infiray_range_request = request_pack(0x02)
    cmd, resp = response_unpack(range_response)
    print(resp['d'])

    print(range(resp['d']) * 3)

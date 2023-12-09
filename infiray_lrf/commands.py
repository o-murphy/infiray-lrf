"""
Typedefs for the InfiRay LR2000 / LR3000 protocol commands
(C) 2023 Yaroshenko Dmytro (https://github.com/o-murphy)
"""

from datetime import datetime

from construct import *

HEADER = Const(b'\xee\x16')

COMMAND = Enum(
    Byte,

    SelfInspection=0x01,
    SingleRanging=0x02,
    SetFirstLast=0x03,  # "Set first / last / multiple targets "
    ContinuousRanging=0x04,
    StopRanging=0x05,

    RangingAbnormal=0x06,  # only responce

    SetBaudRate=0xa0,

    SetFrequency=0xa1,  # "Set continuous ranging_cmd frequency"

    SetMinGate=0xa2,  # "Set minimum gating distance"
    GetMinGate=0xa3,  # "Query minimum gating distance"

    SetMaxGate=0xa4,  # "Maximum gating distance"
    GetMaxGate=0xa5,  # "Query the maximum gating distance"

    FpgaVer=0xa6,  # "Query FPGA software version number"
    McuVer=0xa7,  # "Query MCU software version number"
    HWVer=0xa8,  # "Query hardware version number"
    SN=0xa9,  # "Query Sn number"
    TotalCount=0x90,  # "Total times of light resp put "
    PowerCount=0x91,  # "Query the power on and light resp times this time"
)

TSelfStatus = BitsSwapped(BitStruct(
    fpga_status=Enum(Bit,
                     normal=1,
                     exception=0),
    laser_light_out=Enum(Bit,
                         light_out=1,
                         no_light=0),
    main_wave_detection=Enum(Bit,
                             main_wave=1,
                             no_main_wave=0),
    echo_detection=Enum(Bit,
                        main_wave=1,
                        no_echo=0),
    bias_switch=Enum(Bit,
                     bias_on=1,
                     bias_of=0),
    bias_out=Enum(Bit,
                  voltage_normal=1,
                  abnormal=0),
    temperature=Enum(Bit,
                     normal=1,
                     exception=0),
    _reserve=Bit
))

TSelfInspect = Struct(
    _reserved=Byte,  # reserved
    echo_intensity=Byte,
    system=TSelfStatus,
    status0=BitStruct(
        v5_power=Enum(Bit,
                      normal=1,
                      exception=0),
        _reserve=Bit[7]
    ),
)

TRangingResponse = Struct(
    status=Byte,  # FIXME: make it as Enum
    _range=Int16sb,
    _dec=Int8sb,
    range=Computed(lambda ctx: ctx._range + ctx._dec / 10),
)

TRangingAnomaly = Struct(
    Bytes(3),
    status1=TSelfStatus
)

TSetFirstLast = Enum(
    Byte,
    first=0x01,
    last=0x02,
    multiple=0x03,
)

TSetFrequency = Struct(
    freq=Byte,  # 0x01~0x0A (1-10)
    num=Const(0x00, Byte),  # reserve
)

ChipVer = Struct(
    _ver=BitsSwapped(BitStruct(
        minor=BitsInteger(4),
        major=BitsInteger(4)
    )),
    ver=Computed(lambda ctx: f"{ctx._ver.major}.{ctx._ver.minor}"),
    _day=Byte,
    _my=BitsSwapped(BitStruct(
        m=BitsInteger(4),
        y=BitsInteger(4),
        # year=Computed(lambda ctx: ctx._year + 2020)
    )),
    date=Computed(lambda ctx: datetime(
        ctx._my.y + 2020, ctx._my.m, ctx._day
    ).strftime("%Y-%m-%d")),
)

TFpgaVer = Struct(
    *ChipVer.subcons,
    author=Enum(Byte, cliu=0x6c, dwu=0x5d, cycheng=0xcc),
)

TMcuVer = Struct(
    *ChipVer.subcons,
    author=Enum(Byte, jyang=0x00, llfu=0xf1, zqxiong=0x01),
)

THWVer = Struct(
    MBVS=Byte,
    CTVS=Byte,
    Apdvs=Byte,
    _LDVS=BitsSwapped(BitStruct(
        minor=BitsInteger(4),
        major=BitsInteger(4),
    )),
    LDVS=Computed(lambda ctx: f"{ctx._LDVS.major}.{ctx._LDVS.minor}")
)


def format_sn(ctx):
    date = datetime(ctx._my.y + 2020, ctx._my.m, 1).strftime("%Y%m")
    num = f"{ctx._Num:04.0f}"
    return f"{date}{num}"


_get_sn = Struct(
    _my=BitStruct(
        m=BitsInteger(4),
        y=BitsInteger(4),
    ),
    _Num=Int16sb,

    SN=Computed(format_sn),
)


def crc(ctx):
    if ctx._building:
        data = ctx._io.getvalue()
        return sum(data[3:]) & 0xFF
    if ctx._parsing:
        data = ctx._io.getvalue()
        return sum(data[3:-1]) & 0xFF
    return 0xFF


command_request_struct = Struct(
    HEADER,
    _length=Default(Byte, 0x00),
    _equip=Const(0x03, Byte),
    cmd=COMMAND,
    params=Switch(
        this.cmd, {
            # COMMAND.SelfInspection: TSelfInspect,
            COMMAND.SetFirstLast: TSetFirstLast,
            COMMAND.SetFrequency: TSetFrequency,

            COMMAND.SetMinGate: Int16sb,
            COMMAND.SetMaxGate: Int16sb,

            COMMAND.SetBaudRate: Int32sb,
        },
        default=Const(b'')
    ),
    _size=Tell,
    _length_p=Pointer(HEADER.sizeof(), Rebuild(Byte, this._size - 3)),
    _crc=Rebuild(Checksum(Byte, crc, lambda ctx: ctx), 0)
)

command_response_struct = Struct(
    HEADER,
    _length=Default(Byte, 0x00),
    _equip=Const(0x03, Byte),
    cmd=COMMAND,
    params=Switch(
        this.cmd, {
            COMMAND.SelfInspection: TSelfInspect,
            COMMAND.SetFirstLast: TSetFirstLast,

            COMMAND.SingleRanging: TRangingResponse,
            COMMAND.ContinuousRanging: TRangingResponse,
            COMMAND.RangingAbnormal: TRangingAnomaly,

            COMMAND.GetMinGate: Int16sb,
            COMMAND.SetMinGate: Int16sb,
            COMMAND.GetMaxGate: Int16sb,
            COMMAND.SetMaxGate: Int16sb,

            COMMAND.FpgaVer: TFpgaVer,
            COMMAND.McuVer: TMcuVer,
            COMMAND.HWVer: THWVer,
            COMMAND.SN: _get_sn,
            COMMAND.TotalCount: BitStruct(BitsInteger(24)),
            COMMAND.PowerCount: BitStruct(BitsInteger(24)),

            COMMAND.SetBaudRate: Int32sb  # 115200 / 57600 / 9600
        },
        default=Const(b'')
    ),
    _size=Tell,
    _length_p=Pointer(HEADER.sizeof(), Rebuild(Byte, this._size - 3)),
    _crc=Rebuild(Checksum(Byte, crc, lambda ctx: ctx), 0)
)

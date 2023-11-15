from construct import Struct, Byte, Const, Checksum, BitStruct, Bit, Enum, Bytes, Int8sb, Int16sb, Computed, Default, \
    Rebuild, len_, Tell, Padding
from construct import Switch, this, Pointer


def crc(ctx):
    if ctx._building:
        data = ctx._io.getvalue()
        return sum(data[3:]) & 0xFF
    #     ctx.pop('crc')
    #     data = Struct(*ctx._subcons).build(ctx)
    #     print(data)

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

    RangingAbnormal=0x06,  # only responce

    SetBaudRate=0xa0,
    SetFrequency=0xa1,  # "Set continuous ranging_cmd frequency",
    SetMinGate=0xa2,  # "Set minimum gating distance",
    GetMinGate=0xa3,  # "Query minimum gating distance",
    MaxGate=0xa4,  # "Maximum gating distance",
    GetMaxGate=0xa5,  # "Query the maximum gating distance",
    FpgaVer=0xa6,  # "Query FPGA software version number",
    McuVer=0xa7,  # "Query MCU software version number",
    HWVer=0xa8,  # "Query hardware version number",
    SN=0xa9,  # "Query Sn number",
    Counter=0x90,  # "Total times of light respput ",
    PowerLight=0x91,  # "Query the power on and light resp times this time"
)

HEADER = Const(b'\xee\x16')

ranging_response = Struct(
    HEADER,
    'length' / Byte,
    'equip' / Const(0x3, Byte),
    'command' / command,
    'status' / Byte,
    '_range' / Int16sb,
    '_dec' / Int8sb,
    'range' / Computed(lambda ctx: ctx._range + ctx._dec / 10),
    'crc' / Checksum(Byte, crc, lambda ctx: ctx)
)

# self_inspection_ctrl = Struct(
#     HEADER,
#     Const(b'\x02\x03\x01\x04')
# )

# print(self_inspection_ctrl.build({}))


self_inspection_ctrl = Struct(
    HEADER,
    length=Const(0x02, Byte),
    equip=Const(0x03, Byte),
    cmd=Const(0x01, Byte),
    crc=Checksum(Byte, crc, lambda ctx: ctx)
)


# self_inspection_ret = Struct(
#     HEADER,
#     length=Const(0x06, Byte),
#     equip=Const(0x03, Byte),
#     cmd=Const(0x01, Byte),
#     status3=Byte,  # reserved
#     status2=Byte,
#     status1=BitStruct(
#         fpga_status=Enum(Bit,
#                          normal=1,
#                          exception=0),
#         laser_light_out=Enum(Bit,
#                              light_out=1,
#                              no_light=0),
#         main_wave_detection=Enum(Bit,
#                                  main_wave=1,
#                                  no_main_wave=0),
#         echo_detection=Enum(Bit,
#                             main_wave=1,
#                             no_echo=0),
#         bias_switch=Enum(Bit,
#                          bias_on=1,
#                          bias_of=0),
#         bias_out=Enum(Bit,
#                       voltage_normal=1,
#                       abnormal=0),
#         temperature=Enum(Bit,
#                          normal=1,
#                          exception=0),
#     ),
#     status0=BitStruct(
#         v5_power=Enum(Bit,
#                       normal=1,
#                       exception=0),
#         reserve=Bit[7]
#     ),
#     crc=Checksum(Byte, crc, lambda ctx: ctx)
# )

ranging_ctrl = Enum(
    Bytes(4),
    single=b'\x02\x03\x02\x05',
    continuous=b'\x02\x03\x04\x07',
    stop=b'\x02\x03\x05\x08',
)

ranging_cmd = Struct(HEADER, cmd=ranging_ctrl)

set_frequency = Struct(
    HEADER,
    length=Const(0x04, Byte),
    equip=Const(0x03, Byte),
    cmd=Default(command, command.SetFrequency),
    freq=Byte,  # 0x01~0x0A (1-10)
    num=Const(0x00, Byte),  # reserve
    crc=Checksum(Byte, crc, lambda ctx: ctx)
)

frequency = Struct(
    HEADER,
    length=Const(0x02, Byte),
    equip=Const(0x03, Byte),
    cmd=Default(command, command.SetFrequency),
    crc=Checksum(Byte, crc, lambda ctx: ctx)
)

_self_status = BitStruct(
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
    )

_self_inspect = Struct(
    status3=Byte,  # reserved
    status2=Byte,
    status1=_self_status,
    status0=BitStruct(
        v5_power=Enum(Bit,
                      normal=1,
                      exception=0),
        reserve=Bit[7]
    ),
)


_ranging_response = Struct(
    status=Byte,  # FIXME: make it as Enum
    _range=Int16sb,
    _dec=Int8sb,
    range=Computed(lambda ctx: ctx._range + ctx._dec / 10),
)


_ranging_anomaly = Struct(
    Bytes(3),
    status1=_self_status
)


_set_first_last = Enum(
    Byte,
    first=0x01,
    last=0x02,
    multiple=0x03,
)

_set_freq = Struct(
    freq=Byte,  # 0x01~0x0A (1-10)
    num=Const(0x00, Byte),  # reserve
)


def _crc(ctx):
    data = ctx._io.getvalue()
    return sum(data[3:-1]) & 0xFF


command_request_struct = Struct(
    HEADER,
    length=Default(Byte, 0x00),
    equip=Const(0x03, Byte),
    cmd=command,
    params=Switch(
        this.cmd, {
            command.SelfInspection: _self_inspect,
            command.SetFirstLast: _set_first_last,
            command.SetFrequency: _set_freq,
        },
        default=Const(b'')
    ),
    _size=Tell,
    _length_p=Pointer(HEADER.sizeof(), Rebuild(Byte, this._size - 3)),
    crc=Rebuild(Checksum(Byte, _crc, lambda ctx: ctx), 0)
)


command_response_struct = Struct(
    HEADER,
    length=Default(Byte, 0x00),
    equip=Const(0x03, Byte),
    cmd=command,
    params=Switch(
        this.cmd, {
            command.SelfInspection: _self_inspect,
            command.SetFirstLast: _set_first_last,

            command.SingleRanging: _ranging_response,
            command.ContinuousRanging: _ranging_response,
            command.StopRanging: _ranging_response,
            command.RangingAbnormal: _ranging_anomaly,

            command.SetFrequency: _set_freq,
        },
        default=Const(b'')
    ),
    _size=Tell,
    _length_p=Pointer(HEADER.sizeof(), Rebuild(Byte, this._size - 3)),
    crc=Rebuild(Checksum(Byte, _crc, lambda ctx: ctx), 0)
)


# command_request_struct.build({'cmd': command.SingleRanging, 'params': None})
# command_request_struct.build({'cmd': command.SetFrequency, 'params': {'freq': 1}})

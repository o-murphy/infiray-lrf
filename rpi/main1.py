try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    from rpi.fake_machine import UART, ADC, Pin
    from rpi.parser import response_unpack

except ImportError:
    from machine import UART, ADC, Pin
    from parser import response_unpack


import time


uart_dev = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
uart_lrf = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

led = Pin('LED', Pin.OUT)
led.on()

pot = ADC(Pin(26))

time_init = time.time()


def run_time():
    return int((time.time() - time_init) * 100) / 100


def log(msg):
    print(f"{run_time()}\t{msg}")
    with open('log.txt', 'a') as fp:
        fp.write(f"{run_time()}\t{msg}\n")


async def upd_acp_value():
    prev_pot = 0
    while True:
        pot_value = (pot.read_u16() * 3.3) / 65535
        if pot_value - prev_pot >= 0.01:
            log(f"lr5v {pot_value}")
            prev_pot = pot_value
        await asyncio.sleep(0.02)


async def blink(period, duration):
    for i in range(duration):
        led.off()
        await asyncio.sleep(period)
        led.on()
        await asyncio.sleep(period)


# Coroutine for reading from uart0 and writing to uart1
async def uart0_to_uart1():
    while True:
        try:
            data = uart_dev.read(1)
            if data == b'\xee':
                await asyncio.sleep(0.02)
                data += uart_dev.read(2)
                if data:
                    expected_length = data[2] + 1
                    data += uart_dev.read(expected_length)
                    log(f"dev > dongle {data}")
                    uart_lrf.write(data)
                    log(f"dongle > lr {data}")
        except Exception:
            await blink(1, 1)
        await asyncio.sleep(0.02)


# Coroutine for reading from uart1 and writing to uart0
async def uart1_to_uart0():
    while True:
        try:
            data = uart_lrf.read(1)
            if data == b'\xee':
                await asyncio.sleep(0.02)
                data += uart_lrf.read(2)
                if data:
                    expected_length = data[2] + 1
                    data += uart_lrf.read(expected_length)
                    log(f"lr > dongle {data}")
                    cmd, result = response_unpack(data)
                    if cmd in (0x02, 0x04) and result['s'] != 0x06:
                        _out = (str(result['r']) + '\n').encode('ascii')
                        uart_dev.write(_out)
                        log(f"dongle > dev {_out}")
        except Exception:
            await blink(1, 1)
        await asyncio.sleep(0.02)


# Run both coroutines
async def main():
    task1 = asyncio.create_task(uart0_to_uart1())
    task2 = asyncio.create_task(uart1_to_uart0())
    task3 = asyncio.create_task(upd_acp_value())

    await asyncio.gather(task1, task2, task3)

# Run the event loop
asyncio.run(main())

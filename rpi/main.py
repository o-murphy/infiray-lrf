
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    from rpi.fake_machine import UART, ADC, Pin, freq
    from rpi.parser import response_unpack

except ImportError:
    from machine import UART, ADC, Pin, freq
    from parser import response_unpack

import time


# freq(48000000)

uart_dev = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
uart_lrf = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

led = Pin('LED', Pin.OUT)
led.on()

pot = ADC(Pin(26))

time_init = time.time_ns()


def run_time():
    return int((time.time_ns() - time_init) * 1e-6) / 1000


def log(msg):
    print(f"{run_time()}\t{msg}")
    with open('log.txt', 'a') as fp:
        fp.write(f"{run_time()}\t{msg}\n")


async def upd_acp_value():
    prev_pot = 0
    while True:
        pot_value = (pot.read_u16() * 3.3) / 65535 * 1.52
        if abs(pot_value - prev_pot) >= 0.5:
            log(f"lr5v {pot_value}")
            prev_pot = pot_value
        await asyncio.sleep(0.01)


async def blink(period, duration):
    for i in range(duration):
        led.off()
        await asyncio.sleep(period)
        led.on()
        await asyncio.sleep(period)


async def uart2uart(uart0, uart1):
    while True:
        try:
            data = uart0.read(1)
            if data == b'\xee':
                await asyncio.sleep(0.02)
                data += uart0.read(2)
                await asyncio.sleep(0.02)
                if data:
                    expected_length = data[2] + 1
                    data += uart_dev.read(expected_length)
                    data = process_data(data)
                    uart1.write(data)
        except Exception as e:
            log(err)
            await blink(1, 1)
        await asyncio.sleep(0.02)


# Run both coroutines
async def main():
    task1 = asyncio.create_task(uart2uart(uart0=uart_lrf, uart1=uart_dev))
    task2 = asyncio.create_task(uart2uart(uart0=uart_dev, uart1=uart_lrf))
    task3 = asyncio.create_task(upd_acp_value())

    await asyncio.gather(task1, task2, task3)


# Run the event loop
asyncio.run(main())


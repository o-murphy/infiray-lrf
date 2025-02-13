from machine import UART, I2C, Pin

# buttons init
boot_button = Pin(0, Pin.IN, Pin.PULL_UP)
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)

uart = UART(1, baudrate=115200, tx=Pin(17), rx=Pin(16))
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

lrf_en = Pin(2, Pin.OUT)

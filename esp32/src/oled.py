from machine import I2C, Pin
from src.ssd1306 import SSD1306_I2C
from src.writer import Writer
from src.fonts import font10


# oled init
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)



wri = Writer(oled, font10)


def hline(y, x0=0, x1=oled_width, col=1):
    for i in range(x0, x1):
        oled.pixel(i, y, col)


def vline(x, y0=0, y1=oled_height, col=1):
    for i in range(y0, y1):
        oled.pixel(x, i, col)


def rect(x0=0, y0=0, x1=oled_width, y1=oled_height, col=0):
    hline(y0, x0, x1)
    hline(y1, x0, x1)
    vline(x0, y0, y1)
    vline(x1, y0, y1)


def fill_rect(x0=0, y0=0, x1=oled_width, y1=oled_height, col=0):
    for y in range(y0, y1):
        hline(y, x0, x1, col)


def text(txt, x, y, inv=False, font=None):
    if font:
        wri.font = font
    col = 0 if not inv else 1
    fill_rect(y0=y, y1=wri.font.height(), col=col)
    wri.set_textpos(oled, y, x)
    wri.printstring(txt, inv)
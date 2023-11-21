# OTA

from machine import I2C, Pin
from src.ssd1306 import SSD1306_I2C
from src.writer import Writer
from src.fonts import font10
import framebuf


# oled init
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)
oled.rotate(0)


wri = Writer(oled, font10)


def hline(y, x0=0, x1=oled_width, col=1):
    for i in range(x0, x1):
        oled.pixel(i, y, col)


def text(txt, x, y, inv=False, font=None):
    if font:
        wri.font = font
    wri.set_textpos(oled, y, x)
    wri.printstring(txt, inv)


def draw_range_rect():
    fb = framebuf.FrameBuffer(bytearray(88 * 36 * 2), 88, 36, framebuf.MONO_VLSB)
    fb.fill(0)
    fb.rect(0, 0, 88, 36, 1)
    oled.blit(fb, 40, 14)


def draw_top_rect():
    fb = framebuf.FrameBuffer(bytearray(128 * 13 * 2), 128, 13, framebuf.MONO_VLSB)
    fb.fill(0)
    # fb.rect(0, 0, 128, 13, 0)
    oled.blit(fb, 0, 0)


def draw_bottom_rect():
    fb = framebuf.FrameBuffer(bytearray(128 * 14 * 2), 128, 14, framebuf.MONO_VLSB)
    fb.fill(0)
    # fb.rect(0, 0, 128, 13, 0)
    oled.blit(fb, 0, oled_height-14)


def draw_spin_rect():
    fb = framebuf.FrameBuffer(bytearray(40 * 34 * 2), 40, 34, framebuf.MONO_VLSB)
    fb.fill(0)
    oled.blit(fb, 0, 15)

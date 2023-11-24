import time

import framebuf
from src.fonts import font10, courier20, font6, freesans20
from src.pinout import *
from src.ssd1306 import SSD1306_I2C
from src.writer import Writer

# oled init
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)
oled.rotate(0)

wri = Writer(oled, font10)


class Spinner:
    # states = "\/-"
    _states = ["===", ">==", ">>=", ">>>", "=>>", "==>",
               "===", "==<", "=<<", "<<<", "<<=", "<=="]

    def __init__(self, idx=0, states=None):
        self.idx = idx
        self.states = states if states else self._states

    def next(self):
        self.idx += 1
        if self.idx == len(self.states):
            self.idx = 0
        return self.states[self.idx]


def show_hello():
    oled.fill(0)
    text('ARCHER', 22, 0, font=courier20)
    text("InfiRay-LRF", 20, 28, font=font10)
    oled.text("by o-murphy", 18, 50)
    oled.show()
    time.sleep(2)


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
    oled.blit(fb, 0, 0)


def draw_bottom_rect():
    fb = framebuf.FrameBuffer(bytearray(128 * 14 * 2), 128, 14, framebuf.MONO_VLSB)
    fb.fill(0)
    oled.blit(fb, 0, oled_height - 14)


def draw_spin_rect():
    fb = framebuf.FrameBuffer(bytearray(40 * 34 * 2), 40, 34, framebuf.MONO_VLSB)
    fb.fill(0)
    oled.blit(fb, 0, 15)


def spin(spinner, idx=None):
    draw_spin_rect()
    if idx:
        spinner.idx = idx
    text(f"{spinner.next()}", 0, (oled_height - freesans20.height()) // 2, False, freesans20)
    oled.show()


def on_state(state):
    draw_top_rect()
    text(state, 0, 0, font=font6)
    oled.show()


def on_result(result):
    draw_range_rect()
    text(result, 50, (oled_height - freesans20.height()) // 2, False, freesans20)
    oled.show()


def on_status(status):
    draw_bottom_rect()
    oled.text(status, 0, oled_height - 13)
    oled.show()


def init_gui():
    oled.fill(0)
    oled.rect(40, 14, 88, 36, 1)
    oled.hline(0, font6.height(), oled_width, 1)
    oled.hline(0, oled_height - font6.height() - 1, oled_width, 1)
    draw_range_rect()
    draw_top_rect()
    draw_bottom_rect()

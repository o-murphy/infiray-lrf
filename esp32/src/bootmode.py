# OTA

"""check boot mode"""
from machine import Pin
import sys, time

boot_button = Pin(0, Pin.IN, Pin.PULL_UP)
# buttons init
button0 = Pin(23, Pin.IN, Pin.PULL_UP)
button1 = Pin(18, Pin.IN, Pin.PULL_UP)


def enable_autoboot():
    _set_autoboot(True)


def disable_autoboot():
    _set_autoboot(False)


def _set_autoboot(value):
    try:
        with open('bootmode', 'wb') as fp:
            fp.write(b'\x01' if value else b'\x00')
    except Exception:
        pass


def is_autoboot():
    try:
        with open('bootmode', 'rb') as fp:
            return fp.read() == b'\x01'
    except Exception:
        return False


def bootmode(oled=None):
    if not is_autoboot():
        if oled:
            oled.fill(0)
            oled.text("Autorun disabled", 0, 0)
            oled.text("Sel. boot mode:", 0, 10)
            oled.text("* short click", 0, 25)
            oled.text("  - normal boot", 0, 35)
            oled.text("* long press", 0, 45)
            oled.text("  - REPL>_", 0, 55)
            oled.show()

        c, s = 0, 0.5
        while True:
            if not button0.value():
                try:
                    from src.ota import update
                    update(oled)
                    return
                except Exception as err:
                    print(err)
                    oled.fill(0)
                    oled.text("Update error", 0, 0)
                    time.sleep(2)
                    return
            if not boot_button.value():
                while not boot_button.value():
                    if c >= 2:
                        disable_autoboot()
                        bootmode_repl(oled)
                    time.sleep(s)
                    c += s
                enable_autoboot()
                return
            time.sleep(0.1)


def bootmode_repl(oled=None):
    if oled:
        oled.fill(0)
        oled.text('REPL>_', 40, 20)
        oled.show()
    sys.exit()

# OTA

try:
  import usocket as socket
except:
  import socket

try:
  import urequests as requests
except:
  import requests
import os
import sys
from time import sleep
import network

import machine
import time


# __version__ = '0.0.1'
upd_url = "https://raw.githubusercontent.com/o-murphy/infiray-lrf/ota/esp32/run.py"

ssid = ''
password = ''
station = network.WLAN(network.STA_IF)
station.active(False)
station.active(True)
station.connect(ssid, password)


def update(oled=None):
    oled.fill(0)

    connect_timeout = 5
    oled.text("Connecting...", 0, 0)
    oled.show()
    while not station.isconnected() and connect_timeout > 0:
        time.sleep(1)
        connect_timeout -= 1

    if not station.isconnected():
        oled.text("No connection", 0, 10)
        oled.text('update skipped', 0, 20)
        oled.show()
        time.sleep(2)
        return

    oled.fill(0)

    oled.text("Connected", 0, 0)
    oled.show()

    oled.text("Download...", 0, 10)
    oled.show()
    response = requests.get(upd_url)
    if response.ok:
        resp_text = response.text
        with open("ota.py", "w") as fp:
            fp.write(resp_text)
        oled.text('OK', 0, 20)
        oled.text('rebooting', 0, 30)
        oled.show()
        time.sleep(2)
        machine.reset()
    else:
        oled.text('Error', 0, 20)
        oled.text('update skipped', 0, 30)
        oled.show()







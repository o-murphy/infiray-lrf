# OTA

try:
    import usocket as socket
except:
    import socket

try:
    import urequests as requests
except:
    import requests

import network

import machine
import time
import json


# __version__ = '0.0.1'
upd_url = "https://raw.githubusercontent.com/o-murphy/infiray-lrf/ota/esp32/"

ssid = 'Wokwi-GUEST'
password = ''

try:
    with open('wlan.cfg', 'r') as fp:
        ssid, password, *_ = fp.read().split('\n')
except Exception:
    pass

station = network.WLAN(network.STA_IF)
station.active(False)
station.active(True)
station.connect(ssid, password)


def get_ota_list(oled):
    try:
        otas = []
        print(upd_url + 'ota.json')
        response = requests.get(upd_url + 'ota.json')
        if response.text.find("[") >= 0:
            otas_li = json.loads(response.text)

            for item in otas_li:
                response1 = requests.get(upd_url + item)
                if response1.text.find("OTA") >= 0:
                    otas.append((item, response1.text))
                else:
                    return []

            return otas
        else:
            oled.text('Error', 0, 20)
            oled.text('update skipped', 0, 30)
            oled.show()
    except Exception:
        return []


def update(oled):
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

    ota_list = get_ota_list(oled)
    if len(ota_list) <= 0:
        oled.text('Error', 0, 20)
        oled.text('update skipped', 0, 30)
        oled.show()
        return

    for item, data in ota_list:
        with open(item, "w") as fp:
            fp.write(data)
        oled.text('OK', 0, 20)
        oled.text('rebooting', 0, 30)
        oled.show()
        time.sleep(2)
        machine.reset()

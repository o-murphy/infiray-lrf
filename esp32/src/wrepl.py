# OTA
import sys

from src.oled import oled

import network
import webrepl

# Set your desired WebREPL name and password
ap_ssid = "infiray-lrf"
ap_password = "infiray1"
wrepl_port = 8266

# Connect to WiFi
ap = network.WLAN(network.AP_IF)
ap.config(essid=ap_ssid, password=ap_password, authmode=network.AUTH_WPA2_PSK)
ap.active(True)

# Start WebREPL with the configured parameters
webrepl.start(password=ap_password, port=wrepl_port)

oled.fill(0)
oled.text('WebREPL>_', 25, 5)
oled.text(f'SSID:{ap_ssid}', 0, 25)
oled.text(f'PASS:{ap_password}', 0, 35)
oled.text(f'IP:  {ap.ifconfig()[0]}', 0, 45)
oled.text(f'PORT:  {wrepl_port}', 0, 55)
oled.show()

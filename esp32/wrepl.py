# OTA

import network
import webrepl

# Set your desired WebREPL name and password
webrepl_cfg = {
    "ssid": "your_wifi_ssid",
    "password": "your_wifi_password",
    "bind-addr": "0.0.0.0",
    "port": 8266,
    "auth-mode": "password",
    "web_repl_pass": "your_webrepl_password",
}

# Connect to WiFi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(webrepl_cfg["ssid"], webrepl_cfg["password"])
while not sta_if.isconnected():
    pass

# Start WebREPL with the configured parameters
webrepl.start(**webrepl_cfg)

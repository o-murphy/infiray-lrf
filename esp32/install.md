```shell
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20190125-v1.10.bin
pip install adafruit-ampy --upgrade
ampy --port COM26 --baud 115200 put .\esp32\boot.py
ampy --port COM26 --baud 115200 put .\esp32\ssd1306.py
ampy --port COM26 --baud 115200 put .\esp32\parser.py
ampy --port COM26 --baud 115200 put .\esp32\main.py
```
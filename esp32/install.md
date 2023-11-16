# instalation script

### Install dependencies and flash micropython
```shell
git clone https://github.com/o-murphy/infiray-lrf
cd infiray-lrf/esp
pip install esptool
pip install adafruit-ampy --upgrade
esptool --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20190125-v1.10.bin
```

### Load the project to the board
```shell
ampy --port /dev/ttyUSB0 --baud 115200 put boot.py
ampy --port /dev/ttyUSB0 --baud 115200 put ssd1306.py
ampy --port /dev/ttyUSB0 --baud 115200 put parser.py
ampy --port /dev/ttyUSB0 --baud 115200 put bootmode
ampy --port /dev/ttyUSB0 --baud 115200 put run.py
ampy --port /dev/ttyUSB0 --baud 115200 put main.py
```

### Update code without removing a main.py
* Run controller
* After logo press the BOOT button
* When the display show "AMPY" run the ampy command from terminal

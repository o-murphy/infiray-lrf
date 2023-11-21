# instalation script

### Install dependencies and flash micropython
```shell
git clone https://github.com/o-murphy/infiray-lrf
cd infiray-lrf
pip install -r esp32/requirements.txt
esptool --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20190125-v1.10.bin
```

### Load the project to the board
```shell
ampy --port /dev/ttyUSB0 --baud 115200 put src
ampy --port /dev/ttyUSB0 --baud 115200 put boot.py
ampy --port /dev/ttyUSB0 --baud 115200 put run.py
ampy --port /dev/ttyUSB0 --baud 115200 put main.py
```

### Update controller firmware
* Run controller with button0 pressed
* With button0 select "WebREPL" option
* Accept "WebREPL" option with button1
* Connect your PC to Access point with requisites displayed on the OLED 
* Run in terminal: `python -m esp_ota`


### Run an emulator
* Run controller with button0 pressed
* With button0 select "emulator" option
* Accept "emulator" option with button1


#### Usefull links
* [oled driver](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py)
* [font writer](https://github.com/peterhinch/micropython-font-to-py/tree/master/writer)
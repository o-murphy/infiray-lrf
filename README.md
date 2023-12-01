# InfiRay-LRF
## Command sender for the InfiRay LR2000 / LR3000 Long Range Finder
[![PyPI Version](https://img.shields.io/pypi/v/infiray-lrf?label=PyPI&logo=pypi)
![Python Version](https://img.shields.io/pypi/pyversions/infiray-lrf?logo=python)
![PyPI Format](https://img.shields.io/pypi/wheel/infiray-lrf?label=wheel)
![PyPI Implementation](https://img.shields.io/pypi/implementation/infiray-lrf)](https://pypi.org/project/infiray-lrf/)

## Table of content
* [Instalation](#instalation)
* [Run console](#run-console)
* [Commands list](#commands-list)
* [ESP32 based tester/emulator](esp32/install.md)


## Instalation

```shell
pip install infiray-lrf
```

## Usage

#### Run console
```shell
# enter infiray-inf UART console
python -m infiray-lrf
```

#### Commands list
```shell
# commands list:
q     - quit
h     - help

i     - self inspection

s     - single ranging
cf <int:frequency> <int:timeout> 
      - continious ranging (frequency 1~10Hz, timout - seconds)
C     - nonstop continious ranging
b     - stop ranging
freq <int:frequency>
      - set continious ranging frequency (1~10Hz)
      
glg   - query minimum gating distance
ghg   - query maximum gating distance
slg <int:distance>
      - set minimum gating distance (10-20000m)
shg <int:distance>
      - set maximum gating distance (10-20000m)

fpga  - query FPGA software version number
mcu   - query MCU software version number
hw    - query hardware version number
sn    - query SN number

total - count of times of light resput
count - count of times of light resput since LRF power up

setbaudrate <int:baudrate>
      - set baudrate value (115200 / 57600 / 9600)
```

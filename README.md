# POD-XIAO-Firmware
This is the firmware for the ESP32S3-XIAO to work with POD.

## Compile and Upload
This project is developed with Arduino IDE and v2.0.14 ESP32 Arduino package. More info about the installation can be found [here](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/#strapping-pins).

## Features
- [x] Remote STM32 firmware upload
- [ ] Drone control protocol
- [ ] Drone info collection and uploading
- [ ] Live video streaming

## About
### Remote STM32 Firmware Upload
The STM32 has a [custom bootloader](https://github.com/Leonana69/POD-Bootloader-H7) flashed at `0x8000000`, it will communicate with the ESP32 through UART. The drone controller firmware is located at `0x8020000` (this number may vary according to `FIRMWARE_START_PAGE` in the bootloader) and the bootloader can update this region. Make sure the real firmware is compiled with the following link config with `FLASH (rx)` starting at `0x8020000`:
```
/* in STM32*_FLASH.ld */
MEMORY
{
... /* other memory regions */
FLASH (rx)      : ORIGIN = 0x8020000, LENGTH = 896K
}
```

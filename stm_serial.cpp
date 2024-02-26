#include "stm_serial.h"
#include "config.h"

HardwareSerial stmSerial(0);

void stmSerialInit() {
  stmSerial.begin(1000000, SERIAL_8N1, STM_RX, STM_TX);
}

void stmSerialSend(uint8_t* data, size_t len) {
    stmSerial.write(data, len);
}


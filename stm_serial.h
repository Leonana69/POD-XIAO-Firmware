#ifndef __STM_SERIAL_H__
#define __STM_SERIAL_H__

#include "main.h"

extern HardwareSerial stmSerial;

void stmSerialInit();
void stmSerialSend(uint8_t* data, size_t len);

#endif
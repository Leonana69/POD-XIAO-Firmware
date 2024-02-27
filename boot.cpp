#include "boot.h"

void bootSTM32Bootloader() {
    digitalWrite(STM_ENABLE, LOW);
    digitalWrite(STM_FLOW_CTRL, HIGH);
    delay(100);
    digitalWrite(STM_ENABLE, HIGH);
}

void bootSTM32Firmware() {
    digitalWrite(STM_ENABLE, LOW);
    digitalWrite(STM_FLOW_CTRL, LOW);
    delay(100);
    digitalWrite(STM_ENABLE, HIGH);
}
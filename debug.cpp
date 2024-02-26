#include "debug.h"

size_t serialWriteWrapper(uint8_t c) {
    // Serial.write returns the number of bytes written, which is typically 1 for successful writing of a single byte.
    return Serial.write(c); 
}
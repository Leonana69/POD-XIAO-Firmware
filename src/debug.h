#ifndef __DEBUG_H__
#define __DEBUG_H__

#include "main.h"
#include "eprintf.h"

#ifndef DEBUG_FMT
#define DEBUG_FMT(FMT) FMT
#endif

size_t serialWriteWrapper(uint8_t c);

#ifdef DEBUG
#define DEBUG_PRINT(FMT, ...) eprintf(serialWriteWrapper, FMT, ## __VA_ARGS__)
#else
#define DEBUG_PRINT(FMT, ...)
#endif

#endif
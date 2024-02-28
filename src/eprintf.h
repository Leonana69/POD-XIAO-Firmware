#include <stdarg.h>
#include <stddef.h> // For size_t
#include <stdint.h> // For uint8_t

#ifndef	__EPRINTF_H__
#define __EPRINTF_H__

/**
 * putc function pointer definition
 */
typedef size_t (*putc_t)(uint8_t c);

/**
 * Light printf implementation
 * @param[in] putcf Putchar function to be used by Printf
 * @param[in] fmt Format string
 * @param[in] ... Parameters to print
 * @return the number of character printed
 */
int eprintf(putc_t putcf, const char * fmt, ...)
    __attribute__ (( format(printf, 2, 3) ));

/**
 * Light printf implementation
 * @param[in] putcf Putchar function to be used by Printf
 * @param[in] fmt Format string
 * @param[in] ap Parameters to print
 * @return the number of character printed
 */
int evprintf(putc_t putcf, const char * fmt, va_list ap);

#endif //__EPRINTF_H__

#ifndef __LINK_H__
#define __LINK_H__

#include "podtp.h"

#define PORT_LOAD_BUFFER 0x01
#define PORT_WRITE_FLASH 0x02

#define PORT_START_STM32_BOOTLOADER 0x01
#define PORT_START_STM32_FIRMWARE 0x02

void linkProcessPacket(PodtpPacket *packet);

#endif // __LINK_H__
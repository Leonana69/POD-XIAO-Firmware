#ifndef __LINK_H__
#define __LINK_H__

#include "podtp.h"

#define PORT_LOAD_BUFFER 0x01
#define PORT_WRITE_FLASH 0x02

typedef struct {
    uint16_t bufferPage;
    uint16_t offset;
} __attribute__((__packed__)) LoadBuffer;

void linkSendPacket(PodtpPacket *packet);
bool linkGetPacket(PodtpPacket *packet, uint8_t c);

#endif // __LINK_H__
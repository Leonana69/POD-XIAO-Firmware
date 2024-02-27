#ifndef __STM_LINK_H__
#define __STM_LINK_H__

#include "main.h"
#include "podtp.h"

extern HardwareSerial stmLink;

void stmLinkInit();
void stmLinkSendPacket(PodtpPacket *packet);
void stmLinkAckQueuePut(PodtpPacket *packet);
PodtpPacket* stmLinkSendReliablePacket(PodtpPacket *packet, int retry = 10);
void stmLinkRxTask(void *pvParameters);

#endif
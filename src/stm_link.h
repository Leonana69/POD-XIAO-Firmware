#ifndef __STM_LINK_H__
#define __STM_LINK_H__

#include "main.h"
#include "podtp.h"

class StmLink {
private:
    QueueHandle_t ackQueue;
    HardwareSerial uartSerial;
    PodtpPacket packetBufferRx;
    PodtpPacket packetBufferTx;
    bool uartParsePacket(uint8_t byte);
public:
    StmLink();
    void sendPacket(PodtpPacket *packet);
    void ackQueuePut(PodtpPacket *packet);
    bool sendReliablePacket(PodtpPacket *packet, int retry = 10);
    void rxTask(void *pvParameters);
};

void stmLinkRxTask(void *pvParameters);

extern StmLink *stmLink;

#endif
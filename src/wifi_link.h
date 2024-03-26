#ifndef __WIFI_LINK_H__
#define __WIFI_LINK_H__

#include "main.h"
#include "podtp.h"

class PacketBuffer {
    static const uint8_t MAX_PACKETS = 20;
public:
    PodtpPacket raw[MAX_PACKETS];
    uint8_t head;
    uint8_t tail;
    PacketBuffer(): head(0), tail(0) {}
    void push(PodtpPacket *packet) {
        raw[head] = *packet;
        head = (head + 1) % MAX_PACKETS;
    }

    PodtpPacket *pop() {
        if (head == tail) {
            return NULL;
        }
        PodtpPacket *packet = &raw[tail];
        tail = (tail + 1) % MAX_PACKETS;
        return packet;
    }

    bool empty() {
        return head == tail;
    }

    uint8_t size() {
        return (head + MAX_PACKETS - tail) % MAX_PACKETS;
    }
};

class WifiLink {
private:
    WiFiServer server;
    WiFiClient client;
    PodtpPacket packetBufferRx;
    bool wifiParsePacket(uint8_t c);
    void tx(PodtpPacket *packet);
    PacketBuffer packetBuffer;
public:
    WifiLink();
    void sendPacket(PodtpPacket *packet);
    void rxTask(void *pvParameters);
};

void wifiLinkRxTask(void *pvParameters);

extern WifiLink *wifiLink;

#endif // __WIFI_LINK_H__
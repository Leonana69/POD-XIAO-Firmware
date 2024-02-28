#ifndef __WIFI_LINK_H__
#define __WIFI_LINK_H__

#include "main.h"
#include "podtp.h"

class WifiLink {
private:
    WiFiServer server;
    WiFiClient client;
    PodtpPacket packetBufferRx;
    bool wifiParsePacket(uint8_t c);
public:
    WifiLink();
    void sendPacket(PodtpPacket *packet);
    void rxTask(void *pvParameters);
};

void wifiLinkRxTask(void *pvParameters);

extern WifiLink *wifiLink;

#endif // __WIFI_LINK_H__
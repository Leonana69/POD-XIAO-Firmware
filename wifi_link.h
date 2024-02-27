#ifndef __WIFI_LINK_H__
#define __WIFI_LINK_H__

#include "main.h"
#include "podtp.h"

void wifiLinkInit();
void wifiServerTask(void *pvParameters);
void wifiSendPacket(PodtpPacket *packet);

#endif // __WIFI_LINK_H__
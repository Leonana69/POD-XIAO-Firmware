#include "wifi_link.h"
#include "link.h"

#define DEBUG
#include "debug.h"

WifiLink *wifiLink;

// const char* WIFI_SSID = "YECL-tplink";
// const char* WIFI_PASSWORD = "08781550";
const char* WIFI_SSID = "LEONA";
const char* WIFI_PASSWORD = "64221771";

WifiLink::WifiLink(): server(80), client() {
	WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    DEBUG_PRINT("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
		delay(500);
		DEBUG_PRINT(".");
	}
	DEBUG_PRINT("\nWiFi connected with IP: %s\n", WiFi.localIP().toString().c_str());
	server.begin();
}

void WifiLink::sendPacket(PodtpPacket *packet) {
    if (!client || !client.connected()) {
        return;
    }
    static uint8_t prefix[3] = {PODTP_START_BYTE_1, PODTP_START_BYTE_2, 0};
    prefix[2] = packet->length;
    client.write(prefix, 3);
    client.write(packet->raw, packet->length);
}

void WifiLink::rxTask(void *pvParameters) {
	while (true) {
		if (!client || !client.connected()) {
			client = server.available();
		}
   		// check for new packet
		if (client && client.connected() && client.available()) {
			while (client.available()) {
				if (wifiParsePacket((uint8_t) client.read())) {
					DEBUG_PRINT("RP: t=%d, p=%d, l=%d\n", packetBufferRx.type, packetBufferRx.port, packetBufferRx.length);
					linkProcessPacket(&packetBufferRx);
				}
			}
		}
		vTaskDelay(20);
	}
}

typedef enum {
    PODTP_STATE_START_1,
    PODTP_STATE_START_2,
    PODTP_STATE_LENGTH,
    PODTP_STATE_RAW_DATA
} WifiLinkState;

bool WifiLink::wifiParsePacket(uint8_t byte) {
    static WifiLinkState state = PODTP_STATE_START_1;
    static uint8_t length = 0;

    switch (state) {
        case PODTP_STATE_START_1:
            if (byte == PODTP_START_BYTE_1) {
                state = PODTP_STATE_START_2;
            }
            break;
        case PODTP_STATE_START_2:
            state = (byte == PODTP_START_BYTE_2) ? PODTP_STATE_LENGTH : PODTP_STATE_START_1;
            break;
        case PODTP_STATE_LENGTH:
            length = byte;
            if (length > PODTP_MAX_DATA_LEN || length == 0) {
                state = PODTP_STATE_START_1;
            } else {
                packetBufferRx.length = 0;
                state = PODTP_STATE_RAW_DATA;
            }
            break;
        case PODTP_STATE_RAW_DATA:
            packetBufferRx.raw[packetBufferRx.length++] = byte;
            if (packetBufferRx.length >= length) {
                state = PODTP_STATE_START_1;
                return true;
            }
            break;
        default:
            // reset state
            state = PODTP_STATE_START_1;
            break;
    }
    return false;
}

void wifiLinkRxTask(void *pvParameters) {
    wifiLink->rxTask(pvParameters);
}
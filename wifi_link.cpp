#include "wifi_link.h"
#include "link.h"
#include <WiFi.h>

#define DEBUG
#include "debug.h"

WiFiServer server(80);
WiFiClient client;

bool wifiGetPacket(PodtpPacket *packet, uint8_t c);

void wifiLinkInit() {
    // const char* WIFI_SSID = "LEONA";
	// const char* WIFI_PASSWORD = "64221771";
	const char* WIFI_SSID = "YECL-tplink";
	const char* WIFI_PASSWORD = "08781550";
	WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
	DEBUG_PRINT("Connecting to WiFi");
	while (WiFi.status() != WL_CONNECTED) {
		delay(500);
		DEBUG_PRINT(".");
	}
	DEBUG_PRINT("\nWiFi connected with IP: %s\n", WiFi.localIP().toString().c_str());
	server.begin();
}

void wifiServerTask(void *pvParameters) {
	PodtpPacket packet;
	int packetCount = 0;
	while (true) {
		if (!client || !client.connected()) {
			client = server.available();
			packetCount = 0;
		}

   		// check for new packet
		if (client && client.connected() && client.available()) {
			while (client.available()) {
				if (wifiGetPacket(&packet, (uint8_t) client.read())) {
					DEBUG_PRINT("Received [%d] packet: type=%d, port=%d, length=%d\n", packetCount, packet.type, packet.port, packet.length);
					linkProcessPacket(&packet);
					packetCount++;
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

bool wifiGetPacket(PodtpPacket *packet, uint8_t c) {
    static WifiLinkState state = PODTP_STATE_START_1;
    static uint8_t length = 0;

    switch (state) {
        case PODTP_STATE_START_1:
            if (c == PODTP_START_BYTE_1) {
                state = PODTP_STATE_START_2;
            }
            break;
        case PODTP_STATE_START_2:
            state = (c == PODTP_START_BYTE_2) ? PODTP_STATE_LENGTH : PODTP_STATE_START_1;
            break;
        case PODTP_STATE_LENGTH:
            length = c;
            if (length > PODTP_MAX_DATA_LEN || length == 0) {
                state = PODTP_STATE_START_1;
            } else {
                packet->length = 0;
                state = PODTP_STATE_RAW_DATA;
            }
            break;
        case PODTP_STATE_RAW_DATA:
            packet->raw[packet->length++] = c;
            if (packet->length >= length) {
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

void wifiSendPacket(PodtpPacket *packet) {
    if (!client || !client.connected()) {
        return;
    }
    static uint8_t prefix[3] = {PODTP_START_BYTE_1, PODTP_START_BYTE_2, 0};
    prefix[2] = packet->length;
    client.write(prefix, 3);
    client.write(packet->raw, packet->length);
}
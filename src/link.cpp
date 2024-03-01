#include "link.h"
#include "stm_link.h"
#include "wifi_link.h"
#include "boot.h"

#define DEBUG
#include "debug.h"

void linkProcessPacket(PodtpPacket *packet) {
    switch (packet->type) {
        case PODTP_TYPE_ACK:
            stmLink->ackQueuePut(packet);
            DEBUG_PRINT("ACK: p=%d, l=%d\n", packet->port, packet->length);
            break;
        case PODTP_TYPE_ERROR:
            DEBUG_PRINT("ERR: p=%d, l=%d\n", packet->port, packet->length);
            stmLink->ackQueuePut(packet);
            break;

        case PODTP_TYPE_ESP32:
            // packets for ESP32 are not sent to STM32
            if (packet->port == PORT_START_STM32_BOOTLOADER) {
                DEBUG_PRINT("Start STM32 Bootloader");
                bootSTM32Bootloader();
            } else if (packet->port == PORT_START_STM32_FIRMWARE) {
                DEBUG_PRINT("Start STM32 Firmware");
                bootSTM32Firmware();
            } else {
                DEBUG_PRINT("Unknown ESP32 packet: p=%d, l=%d\n", packet->port, packet->length);
            }
            break;
        case PODTP_TYPE_BOOT_LOADER:
            DEBUG_PRINT("Bootloader packet: p=%d, l=%d\n", packet->port, packet->length);
            stmLink->sendReliablePacket(packet);
            wifiLink->sendPacket(packet);
            break;
        default:
            DEBUG_PRINT("Unknown packet: t=%d, p=%d, l=%d\n", packet->type, packet->port, packet->length);
            break;
    }
    return;
}
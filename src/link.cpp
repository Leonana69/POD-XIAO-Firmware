#include "link.h"
#include "stm_link.h"
#include "wifi_link.h"
#include "boot.h"

#define DEBUG
#include "debug.h"

void linkProcessPacket(PodtpPacket *packet) {
    switch (packet->type) {
        case PODTP_TYPE_ACK:
            DEBUG_PRINT("ACK: %s, l=%d\n", packet->port == PODTP_PORT_OK ? "OK" : "ERROR", packet->length);
            stmLink->ackQueuePut(packet);
            break;

        case PODTP_TYPE_COMMAND:
            DEBUG_PRINT("Command packet: p=%d, l=%d\n", packet->port, packet->length);
            stmLink->sendPacket(packet);
            break;

        case PODTP_TYPE_ESP32:
            // packets for ESP32 are not sent to STM32
            if (packet->port == PORT_ECHO) {
                DEBUG_PRINT("Echo packet: p=%d, l=%d\n", packet->port, packet->length);
                wifiLink->sendPacket(packet);
            } else if (packet->port == PORT_START_STM32_BOOTLOADER) {
                DEBUG_PRINT("Start STM32 Bootloader");
                bootSTM32Bootloader();
            } else if (packet->port == PORT_START_STM32_FIRMWARE) {
                DEBUG_PRINT("Start STM32 Firmware");
                bootSTM32Firmware();
            } else if (packet->port == PORT_DISABLE_STM32) {
                DEBUG_PRINT("Disable STM32");
                bootSTM32Disable();
            } else if (packet->port == PORT_ENABLE_STM32) {
                DEBUG_PRINT("Enable STM32");
                bootSTM32Enable();
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
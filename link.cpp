#include "link.h"
#include "stm_link.h"
#include "wifi_link.h"
#include "boot.h"

#define DEBUG
#include "debug.h"

void linkProcessPacket(PodtpPacket *packet) {
    PodtpPacket *rslt;
    switch (packet->type) {
        case PODTP_TYPE_ACK:
            stmLinkAckQueuePut(packet);
            DEBUG_PRINT("ACK packet: port=%d, length=%d\n", packet->port, packet->length);
            break;
        case PODTP_TYPE_ERROR:
            DEBUG_PRINT("Error packet: port=%d, length=%d\n", packet->port, packet->length);
            stmLinkAckQueuePut(packet);
            break;

        case PODTP_TYPE_ESP32:
            // packets for ESP32 are not sent to STM32
            if (packet->port == PORT_START_STM32_BOOTLOADER) {
                DEBUG_PRINT("Start STM32 bootloader packet: port=%d, length=%d\n", packet->port, packet->length);
                bootSTM32Bootloader();
            } else if (packet->port == PORT_START_STM32_FIRMWARE) {
                DEBUG_PRINT("Start STM32 firmware packet: port=%d, length=%d\n", packet->port, packet->length);
                bootSTM32Firmware();
            } else {
                DEBUG_PRINT("Unknown ESP32 packet: port=%d, length=%d\n", packet->port, packet->length);
            }
            break;
        case PODTP_TYPE_BOOT_LOADER:
            DEBUG_PRINT("Bootloader packet: port=%d, length=%d\n", packet->port, packet->length);
            rslt = stmLinkSendReliablePacket(packet);
            wifiSendPacket(rslt);
            break;
        default:
            DEBUG_PRINT("Unknown packet: type=%d, port=%d, length=%d\n", packet->type, packet->port, packet->length);
            break;
    }
    return;
}
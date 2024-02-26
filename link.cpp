#include "link.h"
#include "stm_serial.h"

#define DEBUG
#include "debug.h"

void linkSendPacket(PodtpPacket *packet) {
    uint8_t check_sum[2] = { 0 };
    check_sum[0] = check_sum[1] = packet->length;
    uint8_t start_bytes[2] = { PODTP_START_BYTE_1, PODTP_START_BYTE_2 };
    stmSerialSend(start_bytes, 2);
    stmSerialSend(&packet->length, 1);
    for (uint8_t i = 0; i < packet->length; i++) {
        check_sum[0] += packet->raw[i];
        check_sum[1] += check_sum[0];
    }
    stmSerialSend(packet->raw, packet->length);
    stmSerialSend(check_sum, 2);
}

typedef enum {
    PODTP_STATE_START_1,
    PODTP_STATE_START_2,
    PODTP_STATE_LENGTH,
    PODTP_STATE_RAW_DATA,
    PODTP_STATE_CRC_1,
    PODTP_STATE_CRC_2
} LinkState;

bool linkGetPacket(PodtpPacket *packet, uint8_t c) {
    static LinkState state = PODTP_STATE_START_1;
    static uint8_t length = 0;
    static uint8_t check_sum[2] = { 0 };
    if (c != 255)
      DEBUG_PRINT("g %d %d\n", c, state);

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
                check_sum[0] = check_sum[1] = c;
                state = PODTP_STATE_RAW_DATA;
            }
            break;
        case PODTP_STATE_RAW_DATA:
            packet->raw[packet->length++] = c;
            check_sum[0] += c;
            check_sum[1] += check_sum[0];
            if (packet->length >= length) {
                state = PODTP_STATE_CRC_1;
            }
            break;
        case PODTP_STATE_CRC_1:
            state = (c == check_sum[0]) ? PODTP_STATE_CRC_2 : PODTP_STATE_START_1;
            break;
        case PODTP_STATE_CRC_2:
            if (c == check_sum[1]) {
                state = PODTP_STATE_START_1;
                return true;
            }
            break;
    }
    return false;
}
#include "stm_link.h"
#include "config.h"
#include "podtp.h"
#include "link.h"

#define DEBUG
#include "debug.h"

HardwareSerial stmLink(0);
QueueHandle_t stmLinkAckQueue;

bool uartGetPacket(PodtpPacket *packet, uint8_t c);

void stmLinkInit() {
  stmLink.begin(1000000, SERIAL_8N1, STM_RX, STM_TX);
  stmLinkAckQueue = xQueueCreate(3, sizeof(PodtpPacket));
}

void stmLinkAckQueuePut(PodtpPacket *packet) {
    xQueueSend(stmLinkAckQueue, packet, 0);
}

void stmLinkRxTask(void *pvParameters) {
	PodtpPacket packet;
	// // we may need a different linkGetPacket
    uint8_t c;
    while (true) {
        while (stmLink.available()) {
            c = stmLink.read();
            if (uartGetPacket(&packet, c)) {
                linkProcessPacket(&packet);
            }
        }
		vTaskDelay(1);
    }
}

void stmLinkSendPacket(PodtpPacket *packet) {
    static uint8_t tail[2] = { 0xA, 0xD };
    uint8_t check_sum[2] = { 0 };
    check_sum[0] = check_sum[1] = packet->length;
    uint8_t start_bytes[2] = { PODTP_START_BYTE_1, PODTP_START_BYTE_2 };
    stmLink.write(start_bytes, 2);
    stmLink.write(&packet->length, 1);
    for (uint8_t i = 0; i < packet->length; i++) {
        check_sum[0] += packet->raw[i];
        check_sum[1] += check_sum[0];
    }
    stmLink.write(packet->raw, packet->length);
    stmLink.write(check_sum, 2);
    stmLink.write(tail, 2);
}

PodtpPacket* stmLinkSendReliablePacket(PodtpPacket *packet, int retry) {
    static PodtpPacket ack_packet;
    for (int i = 0; i < retry; i++) {
        stmLinkSendPacket(packet);
        xQueueReceive(stmLinkAckQueue, &ack_packet, 100);
        if (ack_packet.type == PODTP_TYPE_ACK) {
            break;
        }
    }
    return &ack_packet;
}

typedef enum {
    PODTP_STATE_START_1,
    PODTP_STATE_START_2,
    PODTP_STATE_LENGTH,
    PODTP_STATE_RAW_DATA,
    PODTP_STATE_CHECK_SUM_1,
    PODTP_STATE_CHECK_SUM_2,
} UartLinkState;

bool uartGetPacket(PodtpPacket *packet, uint8_t c) {
    static UartLinkState state = PODTP_STATE_START_1;
    static uint8_t length = 0;
    static uint8_t check_sum[2] = { 0 };

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
                check_sum[0] = check_sum[1] = length;
                state = PODTP_STATE_RAW_DATA;
            }
            break;
        case PODTP_STATE_RAW_DATA:
            packet->raw[packet->length++] = c;
            check_sum[0] += c;
            check_sum[1] += check_sum[0];
            if (packet->length == length) {
                state = PODTP_STATE_CHECK_SUM_1;
            }
            break;
        case PODTP_STATE_CHECK_SUM_1:
            state = (check_sum[0] == c) ? PODTP_STATE_CHECK_SUM_2 : PODTP_STATE_START_1;
            break;
        case PODTP_STATE_CHECK_SUM_2:
            state = PODTP_STATE_START_1;
            if (check_sum[1] == c) {
                return true;
            }
            break;
    }
    return false;
}
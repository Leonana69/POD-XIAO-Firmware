#include "main.h"
#include "config.h"
#include "stm_link.h"
#include "podtp.h"
#include "link.h"
#include "boot.h"
#include "wifi_link.h"

#define DEBUG
#include "debug.h"

void setup() {
#ifdef DEBUG
	// for print debug message to USB serial
	Serial.begin(115200);
#endif
	pinMode(LED_BUILTIN, OUTPUT);
	pinMode(ESP_LED, OUTPUT);

	pinMode(STM_ENABLE, OUTPUT);
	pinMode(STM_FLOW_CTRL, OUTPUT);

	pinMode(BUTTON, INPUT_PULLUP);

	DEBUG_PRINT("Hello, world!\n");
	wifiLink = new WifiLink();
	stmLink = new StmLink();

	// start bootloader for test
	bootSTM32Bootloader();

	xTaskCreatePinnedToCore(wifiLinkRxTask, "wifiServerTask", 4096, NULL, 1, NULL, 1);
	xTaskCreatePinnedToCore(buttonTask, "buttonTask", 4096, NULL, 1, NULL, 1);
	xTaskCreatePinnedToCore(stmLinkRxTask, "stmLinkRxTask", 4096, NULL, 1, NULL, 1);
}

void buttonTask(void *pvParameters) {
	bool buttonState = false;
	bool bootloader = true;
	while (true) {
	// button test
	if (digitalRead(BUTTON) == LOW) {
		if (!buttonState) {
			buttonState = true;
			digitalWrite(LED_BUILTIN, HIGH);
			DEBUG_PRINT("Button pressed\n");
			if (bootloader) {
				DEBUG_PRINT("Start application\n");
				// start application for test
				bootSTM32Firmware();
				bootloader = false;
			} else {
				DEBUG_PRINT("Start bootloader\n");
				// start bootloader for test
				bootSTM32Bootloader();
				bootloader = true;
			}
		}
	} else {
		if (buttonState) {
			buttonState = false;
			digitalWrite(LED_BUILTIN, LOW);
			DEBUG_PRINT("Button released\n");
		}
	}
	vTaskDelay(20);
	}
}

void loop() {}

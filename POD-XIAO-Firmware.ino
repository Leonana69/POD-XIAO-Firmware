#include "src/main.h"
#include "src/config.h"
#include "src/stm_link.h"
#include "src/podtp.h"
#include "src/link.h"
#include "src/boot.h"
#include "src/wifi_link.h"
#include "src/button.h"

#define DEBUG
#include "src/debug.h"

void setup() {
#ifdef DEBUG
	// for print debug message to USB serial
	Serial.begin(115200);
#endif
	pinMode(LED_BUILTIN, OUTPUT);
	pinMode(ESP_LED_PIN, OUTPUT);
	pinMode(STM_ENABLE_PIN, OUTPUT);
	pinMode(STM_FLOW_CTRL_PIN, OUTPUT);
	pinMode(BUTTON_PIN, INPUT_PULLUP);

	DEBUG_PRINT("Hello, world!\n");
	wifiLink = new WifiLink();
	stmLink = new StmLink();

	bootSTM32Firmware();

	xTaskCreatePinnedToCore(wifiLinkRxTask, "wifiServerTask", 4096, NULL, 1, NULL, 1);
	xTaskCreatePinnedToCore(buttonTask, "buttonTask", 4096, NULL, 1, NULL, 1);
	xTaskCreatePinnedToCore(stmLinkRxTask, "stmLinkRxTask", 4096, NULL, 1, NULL, 1);
}

void loop() {}

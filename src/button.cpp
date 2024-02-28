#include "main.h"
#include "button.h"
#include "boot.h"
#include "config.h"

#define DEBUG
#include "debug.h"

void buttonTask(void *pvParameters) {
	bool buttonState = false;
	bool bootloader = true;
	while (true) {
	// button test
	if (digitalRead(BUTTON_PIN) == LOW) {
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
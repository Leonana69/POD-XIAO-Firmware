#include "config.h"
#include "stm_serial.h"
#include "main.h"
#include <WiFi.h>

#define DEBUG
#include "debug.h"

#define WIFI_

void setup() {
#ifdef DEBUG
  // for print debug message to USB serial
  Serial.begin(115200);
#endif
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(ESP_LED, OUTPUT);

  pinMode(STM_ENABLE, OUTPUT);
  pinMode(STM_FLOW_CTRL, OUTPUT);
  
  pinMode(BUTTON, INPUT_PULLUP);

  stmSerialInit();

  digitalWrite(STM_ENABLE, LOW);
  digitalWrite(STM_FLOW_CTRL, LOW);
  digitalWrite(STM_ENABLE, HIGH);

  DEBUG_PRINT("Hello, world!\n");
#ifdef WIFI
  const char* WIFI_SSID = "LEONA";
  const char* WIFI_PASSWORD = "64221771";
  // const char* WIFI_SSID = "YECL-tplink"
  // const char* WIFI_PASSWORD = "08781550"
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  DEBUG_PRINT("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    DEBUG_PRINT(".");
  }
  DEBUG_PRINT("\nWiFi connected with IP: %s\n", WiFi.localIP().toString().c_str());
#endif
}

void loop() {
  // put your main code here, to run repeatedly:

}

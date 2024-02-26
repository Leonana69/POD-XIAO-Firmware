#include <WiFi.h>
#include "main.h"
#include "config.h"
#include "stm_serial.h"
#include "podtp.h"
#include "link.h"

#define DEBUG
#include "debug.h"

#define WIFI

WiFiServer server(80);
WiFiClient client;

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

  stmSerialInit();

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
  server.begin();
#endif

  // start bootloader for test
  digitalWrite(STM_ENABLE, LOW);
  digitalWrite(STM_FLOW_CTRL, HIGH);
  digitalWrite(STM_ENABLE, HIGH);
}

bool buttonState = false;
PodtpPacket packet;
void loop() {
  if (!client || !client.connected()) {
    client = server.available();
  }

  if (client && client.connected() && client.available()) {
    while (client.available()) {
      if (linkGetPacket(&packet, (uint8_t) client.read()))
        DEBUG_PRINT("Received packet: type=%d, port=%d, length=%d\n", packet.type, packet.port, packet.length);
    }
  }


  if (digitalRead(BUTTON) == LOW) {
    if (!buttonState) {
      buttonState = true;
      digitalWrite(LED_BUILTIN, HIGH);
      DEBUG_PRINT("Button pressed\n");

      packet.type = PODTP_TYPE_BOOT_LOADER;
      packet.port = PORT_LOAD_BUFFER;
      LoadBuffer *lb = (LoadBuffer *)packet.data;
      lb->bufferPage = 2;
      lb->offset = 645;
      packet.length = 1 + sizeof(LoadBuffer) + 5;
      packet.data[sizeof(LoadBuffer)] = 0x01;
      packet.data[sizeof(LoadBuffer) + 1] = 0x02;
      packet.data[sizeof(LoadBuffer) + 2] = 0x03;
      packet.data[sizeof(LoadBuffer) + 3] = 0x04;
      packet.data[sizeof(LoadBuffer) + 4] = 0x05;
      linkSendPacket(&packet);
    }
  } else {
    if (buttonState) {
      buttonState = false;
      digitalWrite(LED_BUILTIN, LOW);
      DEBUG_PRINT("Button released\n");
    }
  }
}

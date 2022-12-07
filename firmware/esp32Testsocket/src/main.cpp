#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include "secrets.h"

#ifndef ssid
  #define ssid "youWIFI"
#endif
#ifndef password
  #define password "yourPassword"
#endif
#ifndef serverIP
  #define serverIP "yourServerIP"
#endif
#ifndef serverPort
  #define serverPort 8000
#endif

// wifi
WiFiClient client;



bool ledState = false;
char msgbuffer[20];

int counter = 0;

void check_wifi() {
  // check wifi status
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected");
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      ledState = !ledState;
      digitalWrite(LED_BUILTIN, ledState);
      Serial.print(".");
    }
  }
}

void check_socket() {
  // check socket status
  if (!client.connected()) {
    Serial.println("Socket not connected");
    client.stop();
    client.connect(serverIP, serverPort);
    while (!client.connected()) {
      delay(500);
      ledState = !ledState;
      digitalWrite(LED_BUILTIN, ledState);
      Serial.print("/");
      check_wifi();
    }
  }
}


void setup() {
  // put your setup code here, to run once:
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(250000);
  while(!Serial);
  Serial.println("Starting");

  // wifi
  WiFi.begin(ssid, password);
  Serial.println("Attempting to Connect to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
    ledState = !ledState;
    digitalWrite(LED_BUILTIN, ledState);
    Serial.print("...");
  }

  Serial.println("Connected to WiFi");

  // socket
  client.connect(serverIP, serverPort);
  Serial.println("Attempting to Connect to Socket");
  while (!client.connected()) {
    delay(100);
    ledState = !ledState;
    digitalWrite(LED_BUILTIN, ledState);
    Serial.print("///");
  }
  Serial.println("Connected to Socket");

  Serial.println("Setup done");
}

void loop() {
  // put your main code here, to run repeatedly:
  ledState = !ledState;
  digitalWrite(LED_BUILTIN, ledState);
  check_socket();
  // send data
  sprintf(msgbuffer, "{user1/led/%d}", ledState);
  client.println(msgbuffer);
  Serial.println(msgbuffer);
  delay(200);


}
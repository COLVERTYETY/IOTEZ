#include <WiFi.h>
#include <HTTPClient.h>
#include <string.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include <Arduino.h>
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
  #define serverPort 8001
#endif


//bme sensor

#define SEALEVELPRESSURE_HPA (1013.25)

float val;

Adafruit_BME680 bme; // I2C

// wifi
WiFiClient client;

// http client
HTTPClient http;

#define GROUP "bme680"

bool ledState = false;
char msgbuffer[8];

int counter = 0;

void check_wifi() {
  // check wifi status
  if (WiFi.status() != WL_CONNECTED) {
    ledState = true;
    digitalWrite(LED_BUILTIN, ledState);
    Serial.println("WiFi not connected");
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
  }
}

void send_data(char* group, char *key, char *value) {
  bool success = false;
  while(!success){
    check_wifi();
    // send put request to server
    http.begin(client, "http://" + String(serverIP) + ":" + String(serverPort) + "/"+ String(group) +"/"+ String(key) + "/" + String(value));
    int httpcode = http.PUT("");
    http.end();
    // check if request was successful
    if (httpcode > 0) {
      Serial.println("HTTP PUT request successful");
      success = true;
    } else {
      Serial.println("HTTP PUT request failed");
      Serial.println("Error code: " + String(httpcode));
      Serial.println("Error message: " + http.errorToString(httpcode));
      delay(1000);
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
  check_wifi();
  Serial.println("Connected to WiFi");

  // bme sensor
  if (!bme.begin()) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    while (1){
      delay(100);
      Serial.println("Could not find a valid BME680 sensor, check wiring!");
    }
  }
  
  // Set up oversampling and filter initialization
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320*C for 150 ms

  Serial.println("Setup done");
}



void loop() {
  // put your main code here, to run repeatedly:
  ledState = !ledState;
  digitalWrite(LED_BUILTIN, ledState);

  // read sensor data
  if (! bme.performReading()) {
    Serial.println("Failed to perform reading 🙁");
    return;
  }

  val = bme.temperature;
  dtostrf(val, 4, 2, msgbuffer);
  send_data(GROUP, "temp", msgbuffer);
  delay(200);
  val = bme.humidity;
  dtostrf(val, 4, 2, msgbuffer);
  send_data(GROUP, "hum", msgbuffer);
  delay(200);
  val = bme.pressure / 100.0F;
  dtostrf(val, 4, 2, msgbuffer);
  send_data(GROUP, "pres", msgbuffer);
  delay(200);
  val = bme.gas_resistance / 1000.0F;
  dtostrf(val, 4, 2, msgbuffer);
  send_data(GROUP, "gas", msgbuffer);
  delay(200);
  val = bme.readAltitude(SEALEVELPRESSURE_HPA);
  dtostrf(val, 4, 2, msgbuffer);
  send_data(GROUP, "alt", msgbuffer);
  Serial.println("Data sent");


  // send data
  delay(100*60*1);
}
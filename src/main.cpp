#include <Arduino.h>
#include <ArduinoJson.h>

const char* PROJECT_ID = "COMPANION_SCREEN_V1";
const char* DEVICE_NAME = "ESP32-C3-COMPANION-SCREEN";

// put function declarations here:
void handleHandshake(JsonDocument& doc);
void sendLog(String message);

void setup() {
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, Serial);
    
    if (!error) {
      if (doc["cmd"].is<const char*>() && doc["cmd"] == "DISCOVER") {
        handleHandshake(doc);
      } else if (doc["type"].is<const char*>() && doc["type"] == "data") {
        // Process received data here
        sendLog("Data command received. Cpu usage: " + String(doc["cpu"].as<int>()) + "%, memory usage: " + String(doc["memory"].as<int>()) + "%, disk usage: " + String(doc["disk"].as<int>()) + "%");
      }
    }
  }
}

// put function definitions here:
void handleHandshake(JsonDocument& doc) {
  if (doc["token"].is<const char*>() && doc["token"] == PROJECT_ID) {
    JsonDocument response;
    response["status"] = "READY";
    response["device"] = DEVICE_NAME;
    serializeJson(response, Serial);
    Serial.println();
  }
}

void sendLog(String message) {
  JsonDocument log;
  log["type"] = "log";
  log["msg"] = message;
  serializeJson(log, Serial);
  Serial.println();
}
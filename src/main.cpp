#include <Arduino.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "splashcreen.h"

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define BUTTON_PIN 10
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

const char* PROJECT_ID = "COMPANION_SCREEN_V1";
const char* DEVICE_NAME = "ESP32-C3-COMPANION-SCREEN";
volatile int currentPage = 0;
const int totalPages = 2;
volatile bool pageChanged = false;
JsonDocument globalData;

// Function declarations
void handleHandshake(JsonDocument& doc);
void sendLog(String message);
void updateDisplay();
void IRAM_ATTR next_page_isr();


void setup() {
  Serial.begin(115200);

  Wire.begin(8, 9);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), next_page_isr, FALLING);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for(;;);
  }

  display.clearDisplay();
  playSplash(display);

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 10);
  display.println("Device ready.");
  display.println("Connecting...");
  display.display();
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
        globalData = doc;
        pageChanged = true;
        //sendLog("Data command received. Cpu usage: " + String(doc["cpu"].as<int>()) + "%, memory usage: " + String(doc["memory"].as<int>()) + "%, disk usage: " + String(doc["disk"].as<int>()) + "%");
      }
    }
  }

  if (pageChanged) {
    updateDisplay();
    pageChanged = false;
  }
}

// Function definitions
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

void updateDisplay() {
  display.clearDisplay();
  display.setCursor(0, 0);

  if (currentPage == 0) {
    display.println("System info");
    display.setCursor(0, 15);
    display.printf("CPU: %d%%", globalData["cpu"] | 0);
    display.drawRect(64, 15, 64, 10, SSD1306_WHITE);
    display.fillRect(64, 15, map(globalData["cpu"] | 0, 0, 100, 0, 64), 10, SSD1306_WHITE);

    display.setCursor(0, 30);
    display.printf("RAM: %d%%", globalData["memory"] | 0);
    display.drawRect(64, 30, 64, 10, SSD1306_WHITE);
    display.fillRect(64, 30, map(globalData["memory"] | 0, 0, 100, 0, 64), 10, SSD1306_WHITE);

    display.setCursor(0, 45);
    display.printf("DISK: %d%%", globalData["disk"] | 0);
    display.drawRect(64, 45, 64, 10, SSD1306_WHITE);
    display.fillRect(64, 45, map(globalData["disk"] | 0, 0, 100, 0, 64), 10, SSD1306_WHITE);
    
  } else {
    display.println("Page 2");
    display.setCursor(0, 20);
    display.printf("TODO...");
  }
  
  display.display();
}

void IRAM_ATTR next_page_isr() {
  static unsigned long last_interrupt_time = 0;
  unsigned long interrupt_time = millis();
  // Debouncing: ignore multiple button presses faster than 200ms
  if (interrupt_time - last_interrupt_time > 200) {
    currentPage = (currentPage + 1) % totalPages;
    pageChanged = true;
  }
  last_interrupt_time = interrupt_time;
}
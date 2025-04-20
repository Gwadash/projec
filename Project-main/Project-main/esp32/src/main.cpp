#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// WiFi Credentials
const char* ssid = "Redmi Note 10 Pro";
const char* password = "Rotondwa2+";

// Backend URL
const char* serverUrl = "http://192.168.35.141:5003/sensor-data";

// Sensor Pins
#define SOIL_SENSOR_PIN 34
#define ONE_WIRE_BUS 13         // DS18B20 connected to GPIO 34
#define IR_SENSOR_PIN 26        // IR sensor OUT connected to GPIO 26
#define LDR_SENSOR_PIN 36       // LDR connected to analog GPIO 36

// DS18B20 Setup
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// ============== Reusable Sender ==============
void sendSensorData(String name, float value) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String json = "{\"name\": \"" + name + "\", \"value\": " + String(value, 2) + "}";
    int responseCode = http.POST(json);

    Serial.print("Sent ");
    Serial.print(name);
    Serial.print(" = ");
    Serial.print(value);
    Serial.print(" | Response code: ");
    Serial.println(responseCode);

    http.end();
  } else {
    Serial.println("WiFi Disconnected - cannot send data.");
  }
}

// ============== Soil Moisture ==============
void readSoilMoisture() {
  int moistureValue = analogRead(SOIL_SENSOR_PIN);
  Serial.print("Soil Moisture: ");
  Serial.println(moistureValue);
  sendSensorData("Soil Moisture Sensor", moistureValue);
}

// ============== Temperature ==============
void readTemperature() {
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);
  if (tempC != DEVICE_DISCONNECTED_C) {
    Serial.print("Temperature: ");
    Serial.println(tempC);
    sendSensorData("Temperature Sensor", tempC);
  } else {
    Serial.println("Sensor Error: DS18B20 not found or disconnected.");
  }
}

// ============== IR Obstacle ==============
void detectObstacle() {
  int irValue = digitalRead(IR_SENSOR_PIN); // HIGH = No obstacle, LOW = Obstacle
  String status = (irValue == LOW) ? "Obstacle Detected" : "No Obstacle";
  Serial.println("IR Sensor: " + status);
  sendSensorData("IR Obstacle Sensor", irValue); // 0 = obstacle, 1 = clear
}

// ============== LDR Light Level ==============
void readLDR() {
  int ldrValue = analogRead(LDR_SENSOR_PIN);
  float intensityPercent = map(ldrValue, 0, 4095, 0, 100); // interpret as % brightness
  Serial.print("LDR Value (Light %): ");
  Serial.println(intensityPercent);
  sendSensorData("LDR Light Sensor", intensityPercent);
}

// ============== Setup ==============
void setup() {
  Serial.begin(115200);

  // Connect WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");

  // Init sensors
  sensors.begin();
  pinMode(IR_SENSOR_PIN, INPUT);
}

// ============== Loop ==============
void loop() {
  readSoilMoisture();
  readTemperature();
  detectObstacle();
  readLDR();
  delay(5000); // Read every 5 seconds
}
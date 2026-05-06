/*
 * MedicSync ESP32 Firmware
 * Tactical Triage and Telemetry System
 *
 * Hardware:
 * - ESP32 Development Board
 * - AD8232 ECG Sensor
 *
 * Wiring:
 * AD8232 OUTPUT → GPIO 34 (Analog input)
 * AD8232 LO+   → GPIO 32 (Digital input for leads-off)
 * AD8232 LO-   → GPIO 33 (Digital input for leads-off)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "pk";
const char* password = "Piyush@2006";

// Backend server details (Make sure to update this IP to match your laptop's current Wi-Fi IP)
const char* serverURL = "http://10.217.236.53:3000/api/vitals"; // Currently set to your laptop's Wi-Fi IP

// AD8232 Pin definitions
const int ECG_OUTPUT_PIN = 34;  // Analog pin for ECG signal
const int LO_PLUS_PIN = 32;     // Digital pin for LO+
const int LO_MINUS_PIN = 33;    // Digital pin for LO-

// Soldier identification
const String SERVICE_NUMBER = "PARA-01-05";

// Heart rate calculation variables
unsigned long lastBeatTime = 0;
int beatCount = 0;
int bpm = 0;
int lastECGValue = 0;
bool rising = false;
const int THRESHOLD = 1000;  // Adjust based on your ECG signal strength

// Timing variables
unsigned long lastTransmitTime = 0;
const unsigned long TRANSMIT_INTERVAL = 2000;  // 2 seconds between transmissions

void setup() {
  Serial.begin(115200);

  // Initialize AD8232 pins
  pinMode(LO_PLUS_PIN, INPUT);
  pinMode(LO_MINUS_PIN, INPUT);
  pinMode(ECG_OUTPUT_PIN, INPUT);

  // Connect to WiFi
  connectToWiFi();

  Serial.println("MedicSync ESP32 Firmware Started");
  Serial.println("Service Number: " + SERVICE_NUMBER);
}

void loop() {
  // Read ECG data continuously
  readECG();

  // Transmit data every 2 seconds
  if (millis() - lastTransmitTime >= TRANSMIT_INTERVAL) {
    transmitVitalData();
    lastTransmitTime = millis();
  }

  // Small delay to avoid overwhelming the system
  delay(10);
}

void readECG() {
  int ecgValue = analogRead(ECG_OUTPUT_PIN);

  // Check if electrodes are properly connected
  bool leadsOff = (digitalRead(LO_PLUS_PIN) == LOW || digitalRead(LO_MINUS_PIN) == LOW);

  if (leadsOff) {
    Serial.println("WARNING: Electrodes not properly connected!");
    bpm = 0;  // Set BPM to 0 if leads are off
    return;
  }

  // Simple heart rate detection (QRS complex detection)
  if (ecgValue > THRESHOLD && lastECGValue <= THRESHOLD && rising) {
    // Detected a beat
    unsigned long currentTime = millis();

    if (lastBeatTime != 0) {
      unsigned long beatInterval = currentTime - lastBeatTime;
      bpm = 60000 / beatInterval;  // Convert ms to BPM
    }

    lastBeatTime = currentTime;
    beatCount++;
    rising = false;
  }

  if (ecgValue < THRESHOLD) {
    rising = true;
  }

  lastECGValue = ecgValue;
}

void transmitVitalData() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
    return;
  }

  // Determine status based on triage logic
  String status = "GREEN";
  int spo2 = 98;  // Simulated SpO2

  if (bpm == 0) {
    // Flatline or sensor disconnect
    status = "RED";
    spo2 = 0;
  } else if (bpm > 110) {
    // Tachycardia
    status = "YELLOW";
    spo2 = 94;
  }

  // Create JSON payload
  DynamicJsonDocument doc(256);
  doc["service_number"] = SERVICE_NUMBER;
  doc["heart_rate"] = bpm;
  doc["spo2"] = spo2;
  doc["status"] = status;
  doc["latitude"] = 29.349600;  // Simulated GPS (Nainital, India)
  doc["longitude"] = 79.549900; // Simulated GPS

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  // Send HTTP POST request
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    Serial.print("Data transmitted successfully. HTTP: ");
    Serial.println(httpResponseCode);
    Serial.print("BPM: ");
    Serial.print(bpm);
    Serial.print(", Status: ");
    Serial.println(status);
  } else {
    Serial.print("Error sending data. HTTP: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}

void connectToWiFi() {
  Serial.println("Connecting to WiFi...");

  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("");
    Serial.println("Failed to connect to WiFi");
  }
}
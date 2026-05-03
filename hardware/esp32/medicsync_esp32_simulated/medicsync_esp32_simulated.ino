/*
 * MedicSync ESP32 Firmware - SIMULATED MODE
 * For testing without AD8232 ECG sensor
 *
 * This version simulates realistic ECG data instead of reading from hardware
 * Perfect for testing the complete system with just ESP32 board
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials - UPDATE THESE!
const char* ssid = "Airtel_Zerotouch";
const char* password = "New393002";

// Backend server details
const char* serverURL = "http://192.168.1.8:3000/api/vitals"; // Change to your computer's IP

// Soldier identification
const String SERVICE_NUMBER = "PARA-01-05";

// Simulation variables
unsigned long lastTransmitTime = 0;
const unsigned long TRANSMIT_INTERVAL = 2000;  // 2 seconds between transmissions

// Heart rate simulation
int simulatedBPM = 75;  // Start with normal heart rate
unsigned long lastBPMChange = 0;
const unsigned long BPM_CHANGE_INTERVAL = 10000; // Change BPM every 10 seconds

// Simulated scenarios
enum Scenario { NORMAL, TACHYCARDIA, BRADYCARDIA, FLATLINE };
Scenario currentScenario = NORMAL;
int scenarioDuration = 0;

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  connectToWiFi();

  Serial.println("MedicSync ESP32 Simulated Mode Started");
  Serial.println("Service Number: " + SERVICE_NUMBER);
  Serial.println("SIMULATION: Generating synthetic ECG data");
  Serial.println("No AD8232 sensor required for testing");
}

void loop() {
  // Update simulation scenario periodically
  updateSimulationScenario();

  // Generate simulated heart rate based on current scenario
  generateSimulatedBPM();

  // Transmit data every 2 seconds
  if (millis() - lastTransmitTime >= TRANSMIT_INTERVAL) {
    transmitVitalData();
    lastTransmitTime = millis();
  }

  // Small delay
  delay(100);
}

void updateSimulationScenario() {
  if (millis() - lastBPMChange >= BPM_CHANGE_INTERVAL) {
    // Cycle through different scenarios for testing
    scenarioDuration++;

    if (scenarioDuration > 4) {
      // Change scenario every 4 cycles (40 seconds)
      switch(currentScenario) {
        case NORMAL:
          currentScenario = TACHYCARDIA;
          Serial.println("Scenario: TACHYCARDIA (High Heart Rate)");
          break;
        case TACHYCARDIA:
          currentScenario = BRADYCARDIA;
          Serial.println("Scenario: BRADYCARDIA (Low Heart Rate)");
          break;
        case BRADYCARDIA:
          currentScenario = FLATLINE;
          Serial.println("Scenario: FLATLINE (No Pulse)");
          break;
        case FLATLINE:
          currentScenario = NORMAL;
          Serial.println("Scenario: NORMAL (Recovered)");
          break;
      }
      scenarioDuration = 0;
    }

    lastBPMChange = millis();
  }
}

void generateSimulatedBPM() {
  // Generate realistic BPM based on current scenario
  switch(currentScenario) {
    case NORMAL:
      // Normal heart rate: 60-100 BPM with small variations
      simulatedBPM = random(60, 101);
      break;

    case TACHYCARDIA:
      // High heart rate: 110-160 BPM (medical emergency)
      simulatedBPM = random(110, 161);
      break;

    case BRADYCARDIA:
      // Low heart rate: 40-55 BPM (concerning)
      simulatedBPM = random(40, 56);
      break;

    case FLATLINE:
      // No heart rate: 0 BPM (critical)
      simulatedBPM = 0;
      break;
  }

  // Add small random fluctuations (±2 BPM)
  simulatedBPM += random(-2, 3);
  simulatedBPM = constrain(simulatedBPM, 0, 200);
}

void transmitVitalData() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
    return;
  }

  // Determine status based on triage logic
  String status = "GREEN";
  int spo2 = 98;  // Simulated SpO2

  if (simulatedBPM == 0) {
    // Flatline
    status = "RED";
    spo2 = 0;
    Serial.println("CRITICAL: No pulse detected!");
  } else if (simulatedBPM > 110) {
    // Tachycardia
    status = "YELLOW";
    spo2 = 94;
    Serial.println("WARNING: High heart rate (" + String(simulatedBPM) + " BPM)");
  } else if (simulatedBPM < 50) {
    // Bradycardia (also concerning)
    status = "YELLOW";
    spo2 = 92;
    Serial.println("WARNING: Low heart rate (" + String(simulatedBPM) + " BPM)");
  } else {
    // Normal
    status = "GREEN";
    spo2 = 98;
    Serial.println("Normal: " + String(simulatedBPM) + " BPM");
  }

  // Create JSON payload
  DynamicJsonDocument doc(256);
  doc["service_number"] = SERVICE_NUMBER;
  doc["heart_rate"] = simulatedBPM;
  doc["spo2"] = spo2;
  doc["status"] = status;

  // Simulate small GPS movements around base coordinates
  doc["latitude"] = 29.349600 + (random(-500, 501) / 1000000.0);
  doc["longitude"] = 79.549900 + (random(-500, 501) / 1000000.0);

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  // Send HTTP POST request
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    Serial.print("✓ Data transmitted. HTTP: ");
    Serial.print(httpResponseCode);
    Serial.print(", BPM: ");
    Serial.print(simulatedBPM);
    Serial.print(", Status: ");
    Serial.println(status);
  } else {
    Serial.print("✗ Error sending data. HTTP: ");
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
    Serial.println("✓ WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("");
    Serial.println("✗ Failed to connect to WiFi");
    Serial.println("Please check WiFi credentials and try again");
  }
}
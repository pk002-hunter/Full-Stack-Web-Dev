// Simulates ESP32 hardware sending data to the backend
const axios = require('axios');

const BACKEND_URL = 'http://localhost:3000/api/vitals';

// Simulated soldier data
const soldiers = [];

// 1 Captain (Main data sending capability / Gateway node)
soldiers.push({
  service_number: 'CAPT-01-01',
  heart_rate: 75,
  spo2: 99,
  status: 'GREEN',
  latitude: 29.3750,
  longitude: 79.5314,
  role: 'CAPTAIN',
  battery: 100,
  signal: 100
});

// 19 Dummy Soldiers
for (let i = 1; i <= 19; i++) {
  soldiers.push({
    service_number: `SOLD-01-${i.toString().padStart(2, '0')}`,
    heart_rate: 70 + Math.floor(Math.random() * 20),
    spo2: 96 + Math.floor(Math.random() * 4),
    status: 'GREEN',
    latitude: 29.3750 + (Math.random() - 0.5) * 0.005,
    longitude: 79.5314 + (Math.random() - 0.5) * 0.005,
    role: 'SOLDIER',
    battery: 80 + Math.floor(Math.random() * 20),
    signal: 70 + Math.floor(Math.random() * 30)
  });
}

// Function to simulate hardware sending data
async function simulateHardware() {
  try {
    // console.log(`\n[CAPTAIN NODE CAPT-01-01] Transmitting data for ${soldiers.length} soldiers...`);

    for (const soldier of soldiers) {
      // Simulate hardware failure/signal loss (5% chance a soldier doesn't send data this tick)
      if (Math.random() < 0.05 && soldier.role !== 'CAPTAIN') {
        continue; // Skip sending data for this soldier (simulating signal drop)
      }

      // Simulate some random variation in heart rate
      const heartRateVariation = Math.floor(Math.random() * 20) - 10;
      soldier.heart_rate = Math.max(40, Math.min(160, soldier.heart_rate + heartRateVariation));

      // Update status based on heart rate (triage logic)
      if (soldier.heart_rate === 0) {
        soldier.status = 'RED';
        soldier.spo2 = 0;
      } else if (soldier.heart_rate > 110 || soldier.heart_rate < 50) {
        soldier.status = 'YELLOW';
        soldier.spo2 = 94;
      } else {
        soldier.status = 'GREEN';
        soldier.spo2 = Math.min(100, soldier.spo2 + (Math.random() > 0.5 ? 1 : -1));
      }

      // Small GPS movements
      soldier.latitude += (Math.random() - 0.5) * 0.0001;
      soldier.longitude += (Math.random() - 0.5) * 0.0001;

      // Drain battery slowly
      if (Math.random() < 0.1) {
        soldier.battery = Math.max(0, soldier.battery - 1);
      }

      // Fluctuate signal strength
      soldier.signal = Math.max(10, Math.min(100, soldier.signal + Math.floor(Math.random() * 11) - 5));

      // Send data
      await axios.post(BACKEND_URL, soldier).catch(() => {});
    }

  } catch (error) {
    console.error('Error sending data:', error.message);
  }
}

// Send data every 1 second (1000 ms)
setInterval(simulateHardware, 1000);

console.log('ESP32 Simulator started. Captain node initialized.');
console.log(`Simulating ${soldiers.length} soldiers with advanced telemetry (battery, signal).`);
console.log('Sending data every 1 second...');
// Simulates ESP32 hardware sending data to the backend
const axios = require('axios');

const BACKEND_URL = 'http://localhost:3000/api/vitals';

// Simulated soldier data
const soldiers = [
  {
    service_number: 'PARA-01-05',
    heart_rate: 82,
    spo2: 98,
    status: 'GREEN',
    latitude: 29.349600,
    longitude: 79.549900
  },
  {
    service_number: 'ECHO-22-11',
    heart_rate: 105,
    spo2: 94,
    status: 'YELLOW',
    latitude: 29.349700,
    longitude: 79.549800
  },
  {
    service_number: 'BRAVO-09-02',
    heart_rate: 75,
    spo2: 99,
    status: 'GREEN',
    latitude: 29.349500,
    longitude: 79.549700
  }
];

// Function to simulate hardware sending data
async function simulateHardware() {
  try {
    const randomSoldier = soldiers[Math.floor(Math.random() * soldiers.length)];

    // Simulate some random variation in heart rate
    const heartRateVariation = Math.floor(Math.random() * 20) - 10;
    randomSoldier.heart_rate = Math.max(40, Math.min(160, randomSoldier.heart_rate + heartRateVariation));

    // Update status based on heart rate (your triage logic)
    if (randomSoldier.heart_rate === 0) {
      randomSoldier.status = 'RED';
      randomSoldier.spo2 = 0;
    } else if (randomSoldier.heart_rate > 110) {
      randomSoldier.status = 'YELLOW';
      randomSoldier.spo2 = 94;
    } else {
      randomSoldier.status = 'GREEN';
      randomSoldier.spo2 = 98;
    }

    console.log('Sending data:', randomSoldier);

    const response = await axios.post(BACKEND_URL, randomSoldier);
    console.log('Response:', response.data);

  } catch (error) {
    console.error('Error sending data:', error.message);
  }
}

// Send data every 2 seconds (matching your hardware spec)
setInterval(simulateHardware, 2000);

console.log('ESP32 Simulator started. Sending data every 2 seconds...');
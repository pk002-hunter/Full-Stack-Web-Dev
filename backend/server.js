const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors({
  origin: ['http://localhost:8000', 'http://127.0.0.1:8000'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  credentials: true
}));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
  next();
});

app.use(bodyParser.json());

// In-memory storage for soldier data
let soldiersData = [
  {
    service_number: 'PARA-01-05',
    heart_rate: 82,
    spo2: 98,
    status: 'GREEN',
    latitude: 29.349600,
    longitude: 79.549900
  }
];

// In-memory storage for medical entries
let medicalEntries = {};

// API endpoint to receive data from ESP32/ESP8266
app.post('/api/vitals', (req, res) => {
  try {
    const vitalData = req.body;

    // Validate required fields
    if (!vitalData.service_number) {
      console.warn('Received vitals without service number:', vitalData);
      return res.status(400).json({ error: 'Service number is required' });
    }

    console.log('✅ Received vitals from hardware:', vitalData);

    // Validate data types
    const validatedData = {
      service_number: String(vitalData.service_number),
      heart_rate: parseInt(vitalData.heart_rate) || 75,
      spo2: parseInt(vitalData.spo2) || 98,
      status: ['RED', 'YELLOW', 'GREEN'].includes(vitalData.status) ? vitalData.status : 'GREEN',
      latitude: parseFloat(vitalData.latitude) || 29.349600,
      longitude: parseFloat(vitalData.longitude) || 79.549900
    };

    // Update or add soldier data
    const existingIndex = soldiersData.findIndex(s => s.service_number === validatedData.service_number);

    if (existingIndex !== -1) {
      soldiersData[existingIndex] = { ...soldiersData[existingIndex], ...validatedData };
      console.log(`📊 Updated soldier ${validatedData.service_number}`);
    } else {
      soldiersData.push(validatedData);
      console.log(`👤 Added new soldier ${validatedData.service_number}`);
    }

    res.status(200).json({ message: 'Vitals received successfully', data: validatedData });
  } catch (error) {
    console.error('❌ Error processing vitals:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// API endpoint for Django frontend to fetch data
app.get('/api/soldiers', (req, res) => {
  res.json(soldiersData);
});

// API endpoint to get medical entries for a soldier
app.get('/api/medical/:service_number', (req, res) => {
  try {
    const { service_number } = req.params;
    const entries = medicalEntries[service_number] || [];
    res.json({ entries });
  } catch (error) {
    console.error('Error fetching medical entries:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// API endpoint to add medical entry
app.post('/api/medical', (req, res) => {
  try {
    const { service_number, injury, treatment, body_part, details, notes } = req.body;

    if (!service_number) {
      return res.status(400).json({ error: 'Service number is required' });
    }

    const entry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      service_number,
      injury: injury || 'Assessment',
      treatment: treatment || 'None',
      body_part: body_part || 'Unknown',
      details: details || '',
      notes: notes || '',
      confirmed: false
    };

    if (!medicalEntries[service_number]) {
      medicalEntries[service_number] = [];
    }

    medicalEntries[service_number].push(entry);

    console.log('✅ Added detailed medical entry:', {
      service_number: entry.service_number,
      injury: entry.injury,
      body_part: entry.body_part,
      treatment: entry.treatment
    });

    res.status(201).json({
      message: 'Medical entry added successfully',
      entry
    });

  } catch (error) {
    console.error('Error adding medical entry:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// API endpoint to confirm medical entries
app.post('/api/medical/confirm', (req, res) => {
  try {
    const { service_number, entry_ids } = req.body;

    if (!service_number || !entry_ids || !Array.isArray(entry_ids)) {
      return res.status(400).json({ error: 'Service number and entry IDs array are required' });
    }

    if (!medicalEntries[service_number]) {
      return res.status(404).json({ error: 'No medical entries found for this soldier' });
    }

    let confirmedCount = 0;
    medicalEntries[service_number].forEach(entry => {
      if (entry_ids.includes(entry.id)) {
        entry.confirmed = true;
        confirmedCount++;
      }
    });

    res.json({
      message: `${confirmedCount} medical entries confirmed successfully`,
      confirmed_count: confirmedCount
    });

  } catch (error) {
    console.error('Error confirming medical entries:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`MedicSync Backend Server running on port ${PORT}`);
  console.log(`API endpoints:`);
  console.log(`  POST /api/vitals - Receive data from hardware`);
  console.log(`  GET  /api/soldiers - Provide data to frontend`);
  console.log(`  GET  /health - Health check`);
});

module.exports = app;
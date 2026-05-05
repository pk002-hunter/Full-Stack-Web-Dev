# MedicSync: The Tactical Triage System 🚑

![MedicSync Banner](https://img.shields.io/badge/Status-Active-brightgreen) ![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue) ![Django Version](https://img.shields.io/badge/Django-4.2%20LTS-darkgreen)

MedicSync is an advanced, highly specialized tactical healthcare application designed specifically to streamline, secure, and accelerate casualty data management in high-pressure, resource-constrained environments. It completely replaces volatile, analog paper tracking (TCCC cards) with a robust, persistent digital pipeline.

By bridging the gap between the point of injury and definitive care, MedicSync minimizes critical data loss, reduces cognitive load on first responders, and radically optimizes MEDEVAC operations during the "Golden Hour" of trauma response.

## 🚀 Key Features

* **Dual-Interface Architecture:** 
  * **Tactical UI:** A touch-optimized, dark-mode single-page interface with massive touch targets designed for medics operating under physical duress and in blackout conditions.
  * **Hospital View:** A centralized, wide-screen optimized dashboard for medical command to track inbound casualties and allocate operating room resources.
* **Offline-First Resilience:** In the event of network denial, the frontend caches all data locally using the browser's IndexedDB. Background fetch routines automatically synchronize queued payloads the instant radio connectivity is restored.
* **Dynamic Geographic Mapping:** Integrates **Leaflet.js** to track and display the exact spatial distribution of casualties in real time. Features algorithmic "debouncing" to prevent network floods when dragging map markers.
* **Bi-Directional Synchronization:** Ensures the edge nodes (medics) and the command server remain perfectly synchronized without requiring manual page refreshes.
* **Strict Security Layers:** Built with Django's ORM to inherently prevent SQL Injection, combined with rigorous payload sanitization and CSRF-token enforcement for administrative actions.

## 🛠️ Technology Stack

MedicSync was deliberately engineered to avoid heavy, fragile dependencies, prioritizing rapid "cold-start" field deployments over arbitrary cloud complexity.

* **Backend API & Logic:** Python 3.10+, Django 4.2 LTS (MVT Architecture)
* **Database:** SQLite 3 (Serverless, zero-configuration portability)
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6) (Zero-dependency for instantaneous load times)
* **Spatial Mapping:** Leaflet.js v1.9+

## ⚙️ Installation & Deployment

MedicSync requires both a Python/Django environment and a Node.js backend to run the full simulation and routing.

### Prerequisites
* **Python 3.10+**
* **Node.js 18+**

### 1. Rapid Deployment (Windows)
For an immediate "cold start" without manual commands, simply double-click the provided batch file:
```bash
start_medicsync.bat
```
*This script will automatically boot up the Node.js backend, the ESP32 simulator, and the Django server, then open the browser to the tactical interface.*

### 2. Manual Setup (Development)
If you prefer to install dependencies and run the system manually:

**Step A: Set up the Python Django Server**
1. **Create a virtual environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   ```
2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Apply database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Start the Django Development Server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

**Step B: Set up the Node.js Backend**
Open a new terminal window and navigate to the backend directory:
1. **Navigate and Install Packages**
   ```bash
   cd backend
   npm install
   ```
2. **Start the Node Server**
   ```bash
   npm start
   ```
*(Optional) You can also run `node simulate-esp32.js` inside the backend folder to simulate incoming hardware telemetry.*

## 📂 System Code Structure

* `/medicsync/` - Core project configurations, security middleware, and primary routing hub.
* `/tactical_ui/` - The business logic hub containing RESTful JSON endpoints (`views.py`) and the SQLite schema mappings (`models.py`).
* `/templates/` - Semantic HTML structures kept completely devoid of logic.
* `/static/` - CSS stylesheets, Vanilla JS synchronization engines, and mapping logic.

## 👥 Project Team

* **Piyush Karnatak** (Backend API & Systems Architect)
* **Rahul Bhakuni** (Frontend UI/UX & Interaction Lead)
* **Vishal Joshi** (Database Engineer & Migration Specialist)
* **Lalit Joshi** (Map Integration & Hospital Admin Developer)

*Graphic Era Hill University, Bhimtal - Department of Computer Science & Engineering (2026-2027)*

## 🔮 Future Roadmap

* **Automated Biometric Integration:** Implementing BLE APIs to ingest real-time data from smart tourniquets and chest-strap heart rate monitors.
* **WebSocket Integration:** Upgrading the asynchronous polling engine to ASGI/Django Channels for true full-duplex event pushing.
* **HL7 FHIR Interoperability:** Ensuring export compatibility with major national Electronic Health Record (EHR) systems.

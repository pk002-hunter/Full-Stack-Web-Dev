#!/usr/bin/env python3
"""
MedicSync System Test Script
Tests the complete system without requiring hardware
"""

import requests
import time
import sys

def test_backend_connection():
    """Test if Node.js backend is running"""
    try:
        response = requests.get("http://localhost:3000/health", timeout=2)
        if response.status_code == 200:
            print("[OK] Node.js backend is running")
            return True
    except requests.RequestException:
        print("[ERROR] Node.js backend not found on port 3000")
        print("   Run: cd backend && npm start")
        return False

def test_django_connection():
    """Test if Django frontend is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            print("[OK] Django frontend is running")
            return True
    except requests.RequestException:
        print("[ERROR] Django frontend not found on port 8000")
        print("   Run: python manage.py runserver")
        return False

def test_api_endpoint():
    """Test if API endpoint is working"""
    try:
        response = requests.get("http://localhost:8000/api/soldiers/", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print("[OK] API endpoint working")
            print(f"   Soldiers data: {data}")
            return True
    except requests.RequestException as e:
        print(f"[ERROR] API endpoint error: {e}")
        return False

def simulate_esp32_data():
    """Simulate ESP32 sending data to backend"""
    test_data = {
        "service_number": "TEST-99-99",
        "heart_rate": 88,
        "spo2": 97,
        "status": "GREEN",
        "latitude": 29.349600,
        "longitude": 79.549900
    }

    try:
        response = requests.post("http://localhost:3000/api/vitals",
                               json=test_data, timeout=2)
        if response.status_code == 200:
            print("[OK] Backend accepted test data")
            return True
    except requests.RequestException:
        print("[ERROR] Could not send test data to backend")
        return False

def main():
    print("MedicSync System Test")
    print("=" * 50)

    backend_ok = test_backend_connection()
    django_ok = test_django_connection()

    if backend_ok:
        api_ok = test_api_endpoint()
        simulate_esp32_data()

    print("\n" + "=" * 50)

    if backend_ok and django_ok:
        print("SUCCESS: System is ready!")
        print("\nNext steps:")
        print("1. Open http://localhost:8000 in your browser")
        print("2. Upload simulated firmware to ESP32")
        print("3. Watch real-time updates every 2 seconds")
    else:
        print("WARNING: Some components need attention")
        print("\nQuick start:")
        print("Terminal 1: cd backend && npm start")
        print("Terminal 2: python manage.py runserver")
        print("Terminal 3: Open browser to http://localhost:8000")

if __name__ == "__main__":
    main()
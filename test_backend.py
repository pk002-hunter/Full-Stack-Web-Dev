#!/usr/bin/env python3
"""
Test script to verify backend connectivity
"""

import requests
import time

def test_backend():
    """Test Node.js backend connection"""
    try:
        response = requests.get("http://localhost:3000/health", timeout=2)
        print(f"Backend health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Backend connection failed: {e}")
        return False

def test_django_api():
    """Test Django API endpoints"""
    try:
        response = requests.get("http://localhost:8000/api/health/", timeout=2)
        print(f"Django health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Django API failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing MedicSync Backend Connectivity")
    print("=" * 50)

    backend_ok = test_backend()

    if backend_ok:
        print("\nTesting Django Frontend API")
        print("-" * 30)
        django_ok = test_django_api()

    print("\n" + "=" * 50)
    if backend_ok:
        print("Backend is running correctly")
    else:
        print("Backend needs attention - run: cd backend && npm start")

    if django_ok:
        print("Django API is working")
    else:
        print("Django needs attention - run: python manage.py runserver")
#!/usr/bin/env python3
"""
Test script to diagnose Django POST issue
"""

import requests
import json

def test_django_post():
    """Test POST request to Django view"""
    url = "http://localhost:8000/api/medical/confirm/"
    data = {
        "service_number": "TEST-99-99",
        "entry_ids": [123]
    }

    headers = {
        "Content-Type": "application/json",
        "Origin": "http://localhost:8000"
    }

    try:
        print("Testing POST to Django view...")
        response = requests.post(url, json=data, headers=headers, timeout=5)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_django_post()
from django.shortcuts import render
import requests
import json
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Configuration for Node.js backend
NODE_BACKEND_URL = 'http://localhost:3000'

def fetch_soldiers_from_backend():
    """Fetch real-time soldier data from Node.js backend"""
    try:
        response = requests.get(f'{NODE_BACKEND_URL}/api/soldiers', timeout=3)
        response.raise_for_status()
        return response.json()
    except:
        # Return simple simulated data
        return [{'service_number': 'TEST-01', 'heart_rate': 75, 'spo2': 98, 'status': 'GREEN', 'latitude': 29.349600, 'longitude': 79.549900}]

def transform_backend_data(backend_data):
    """Transform backend data to match frontend schema"""
    soldiers = []
    for soldier_data in backend_data:
        soldiers.append({
            'id': soldier_data.get('service_number', 'UNKNOWN'),
            'triage': soldier_data.get('status', 'GREEN'),
            'hr': soldier_data.get('heart_rate', 75),
            'spo2': soldier_data.get('spo2', 98),
            'blood_type': 'O+',
            'allergies': 'None',
            'latest_injury': 'Stable',
            'latest_treatment': 'Monitoring',
            'eta': '30',
            'logs': [],
            'latitude': soldier_data.get('latitude', 0),
            'longitude': soldier_data.get('longitude', 0)
        })
    return soldiers

@csrf_exempt
def api_soldiers_view(request):
    """API endpoint for frontend to fetch soldier data"""
    if request.method == 'GET':
        backend_data = fetch_soldiers_from_backend()
        soldiers = transform_backend_data(backend_data)
        return JsonResponse({'soldiers': soldiers})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_health_view(request):
    """API endpoint for health check and system status"""
    if request.method == 'GET':
        try:
            backend_response = requests.get(f'{NODE_BACKEND_URL}/health', timeout=2)
            backend_status = backend_response.status_code == 200
        except:
            backend_status = False

        return JsonResponse({
            'django_status': 'OK',
            'backend_status': 'OK' if backend_status else 'OFFLINE',
            'timestamp': time.time()
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)
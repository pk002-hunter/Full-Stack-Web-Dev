from django.shortcuts import render
import requests
import json
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Configuration for Node.js backend
NODE_BACKEND_URL = 'http://localhost:3000'  # Change this to your Node.js server URL


def fetch_soldiers_from_backend():
    """Fetch real-time soldier data from Node.js backend"""
    try:
        response = requests.get(f'{NODE_BACKEND_URL}/api/soldiers', timeout=3)
        response.raise_for_status()
        return response.json()
    except:
        # Return simulated data for demo
        import time
        current_time = int(time.time())
        scenario = (current_time // 20) % 4

        if scenario == 0:
            return [{'service_number': 'PARA-01-05', 'heart_rate': 78, 'spo2': 98, 'status': 'GREEN', 'latitude': 29.349600, 'longitude': 79.549900}]
        elif scenario == 1:
            return [{'service_number': 'PARA-01-05', 'heart_rate': 125, 'spo2': 94, 'status': 'YELLOW', 'latitude': 29.349700, 'longitude': 79.549800}]
        elif scenario == 2:
            return [{'service_number': 'PARA-01-05', 'heart_rate': 45, 'spo2': 92, 'status': 'YELLOW', 'latitude': 29.349500, 'longitude': 79.549700}]
        else:
            return [{'service_number': 'PARA-01-05', 'heart_rate': 0, 'spo2': 0, 'status': 'RED', 'latitude': 29.349600, 'longitude': 79.549900}]


def transform_backend_data(backend_data):
    """Transform backend data to match frontend schema"""
    soldiers = []
    for soldier_data in backend_data:
        soldiers.append({
            'id': soldier_data.get('service_number', 'UNKNOWN'),
            'triage': soldier_data.get('status', 'GREEN'),
            'hr': soldier_data.get('heart_rate', 75),
            'spo2': soldier_data.get('spo2', 98),
            'blood_type': 'O+',  # Hardcoded for now
            'allergies': 'None',  # Hardcoded for now
            'latest_injury': get_latest_injury(soldier_data),
            'latest_treatment': 'Monitoring',  # Placeholder
            'eta': calculate_eta(soldier_data),
            'logs': [],
            'latitude': soldier_data.get('latitude', 0),
            'longitude': soldier_data.get('longitude', 0)
        })
    return soldiers


def get_latest_injury(soldier_data):
    """Determine latest injury based on status"""
    status = soldier_data.get('status', 'GREEN')
    if status == 'RED':
        return 'Critical - Monitor Required'
    elif status == 'YELLOW':
        return 'Elevated Heart Rate'
    else:
        return 'Stable - Routine Monitoring'


def calculate_eta(soldier_data):
    """Calculate ETA based on status"""
    status = soldier_data.get('status', 'GREEN')
    if status == 'RED':
        return '5'
    elif status == 'YELLOW':
        return '15'
    else:
        return '30'

def dashboard_view(request):
    backend_data = fetch_soldiers_from_backend()
    soldiers = transform_backend_data(backend_data)
    return render(request, 'dashboard.html', {'soldiers': soldiers})


def casualty_card_view(request, soldier_id):
    backend_data = fetch_soldiers_from_backend()
    soldiers = transform_backend_data(backend_data)
    # Find active soldier or fallback
    soldier = next((s for s in soldiers if s['id'] == soldier_id), soldiers[0] if soldiers else None)
    return render(request, 'casualty_card.html', {'soldier': soldier})


def hospital_standby_view(request):
    backend_data = fetch_soldiers_from_backend()
    soldiers = transform_backend_data(backend_data)
    # Sort by Red first, then Yellow, then Green
    sorted_soldiers = sorted(soldiers, key=lambda x: {'RED': 0, 'YELLOW': 1, 'GREEN': 2}[x['triage']])
    return render(request, 'hospital_view.html', {'soldiers': sorted_soldiers})


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
            # Try to connect to Node.js backend
            backend_response = requests.get(f'{NODE_BACKEND_URL}/health', timeout=2)
            backend_status = backend_response.status_code == 200
        except requests.RequestException:
            backend_status = False

        return JsonResponse({
            'django_status': 'OK',
            'backend_status': 'OK' if backend_status else 'OFFLINE',
            'timestamp': time.time()
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_medical_entries_view(request, soldier_id):
    """API endpoint to get medical entries for a soldier"""
    if request.method == 'GET':
        try:
            response = requests.get(f'{NODE_BACKEND_URL}/api/medical/{soldier_id}', timeout=3)
            response.raise_for_status()
            return JsonResponse(response.json())
        except requests.RequestException as e:
            return JsonResponse({'error': 'Backend unavailable', 'entries': []}, status=503)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_add_medical_entry_view(request):
    """API endpoint to add a medical entry"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            response = requests.post(f'{NODE_BACKEND_URL}/api/medical',
                                   json=data, timeout=3)
            response.raise_for_status()
            return JsonResponse(response.json())
        except requests.RequestException as e:
            return JsonResponse({'error': 'Backend unavailable'}, status=503)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_confirm_medical_view(request):
    """API endpoint to confirm medical entries"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            response = requests.post(f'{NODE_BACKEND_URL}/api/medical/confirm',
                                   json=data, timeout=3)
            response.raise_for_status()
            return JsonResponse(response.json())
        except requests.RequestException as e:
            return JsonResponse({'error': 'Backend unavailable'}, status=503)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def map_view(request):
    """Tactical map overview"""
    return render(request, 'map_view.html')

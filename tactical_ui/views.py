from django.shortcuts import render
import requests
import json
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MedicalEntry

# Configuration for Node.js backend
NODE_BACKEND_URL = 'http://localhost:3000'


def fetch_soldiers_from_backend():
    try:
        response = requests.get(f'{NODE_BACKEND_URL}/api/soldiers', timeout=3)
        response.raise_for_status()
        return response.json()
    except:
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
    soldiers = []
    for soldier_data in backend_data:
        service_number = soldier_data.get('service_number', 'UNKNOWN')

        # Get the latest injury/treatment from Django database (persistent, fast, no network call)
        latest_entry = MedicalEntry.objects.filter(service_number=service_number).first()

        if latest_entry:
            latest_injury = latest_entry.injury or 'Assessment'
            if latest_entry.body_part and latest_entry.body_part != 'Unknown':
                latest_injury = f"{latest_injury} - {latest_entry.body_part}"
            latest_treatment = latest_entry.treatment or 'Monitoring'
        else:
            latest_injury = get_latest_injury(soldier_data)
            latest_treatment = 'Monitoring'

        # Get all medical entries (logs) for this soldier from DB
        logs = list(
            MedicalEntry.objects.filter(service_number=service_number)
            .values('id', 'injury', 'body_part', 'treatment', 'details', 'notes', 'confirmed', 'timestamp')
            [:20]  # Last 20 entries
        )

        soldiers.append({
            'id': service_number,
            'triage': soldier_data.get('status', 'GREEN'),
            'hr': soldier_data.get('heart_rate', 75),
            'spo2': soldier_data.get('spo2', 98),
            'blood_type': 'O+',
            'allergies': 'None',
            'latest_injury': latest_injury,
            'latest_treatment': latest_treatment,
            'eta': calculate_eta(soldier_data),
            'logs': logs,
            'latitude': soldier_data.get('latitude', 0),
            'longitude': soldier_data.get('longitude', 0),
            'role': soldier_data.get('role', 'SOLDIER'),
            'battery': soldier_data.get('battery', 100),
            'signal': soldier_data.get('signal', 100),
            'last_updated': soldier_data.get('last_updated', None)
        })
    return soldiers


def get_latest_injury(soldier_data):
    status = soldier_data.get('status', 'GREEN')
    if status == 'RED':
        return 'Critical - Monitor Required'
    elif status == 'YELLOW':
        return 'Elevated Heart Rate'
    else:
        return 'Stable - Routine Monitoring'

def calculate_eta(soldier_data):
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
    soldier = next((s for s in soldiers if s['id'] == soldier_id), soldiers[0] if soldiers else None)
    return render(request, 'casualty_card.html', {'soldier': soldier})

def hospital_standby_view(request):
    backend_data = fetch_soldiers_from_backend()
    soldiers = transform_backend_data(backend_data)
    sorted_soldiers = sorted(soldiers, key=lambda x: {'RED': 0, 'YELLOW': 1, 'GREEN': 2}[x['triage']])
    return render(request, 'hospital_view.html', {'soldiers': sorted_soldiers})

@csrf_exempt
def api_soldiers_view(request):
    if request.method == 'GET':
        backend_data = fetch_soldiers_from_backend()
        soldiers = transform_backend_data(backend_data)
        return JsonResponse({'soldiers': soldiers})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_health_view(request):
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

@csrf_exempt
def api_medical_entries_view(request, soldier_id):
    """Get all medical entries for a soldier from Django DB."""
    if request.method == 'GET':
        entries = MedicalEntry.objects.filter(service_number=soldier_id)
        entries_list = [entry.to_dict() for entry in entries]
        return JsonResponse({'entries': entries_list})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_add_medical_entry_view(request):
    """Save a medical entry to Django DB AND forward to Node.js backend."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Save to Django database (persistent storage)
            entry = MedicalEntry.objects.create(
                service_number=data.get('service_number', ''),
                injury=data.get('injury', 'Assessment'),
                body_part=data.get('body_part', 'Unknown'),
                treatment=data.get('treatment', ''),
                details=data.get('details', ''),
                notes=data.get('notes', ''),
            )

            # Also forward to Node.js backend (best effort, don't fail if it's down)
            try:
                requests.post(f'{NODE_BACKEND_URL}/api/medical', json=data, timeout=2)
            except:
                pass  # Node.js backend is optional for medical entries

            return JsonResponse({
                'message': 'Medical entry saved successfully',
                'entry': entry.to_dict()
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error saving entry: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_confirm_medical_view(request):
    """Confirm medical entries in Django DB."""
    if request.method == 'POST':
        try:
            body_str = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            data = json.loads(body_str)

            service_number = data.get('service_number')
            entry_ids = data.get('entry_ids', [])

            if not service_number:
                return JsonResponse({'error': 'Missing required field: service_number'}, status=400)

            # Confirm all unconfirmed entries for this soldier in Django DB
            updated = MedicalEntry.objects.filter(
                service_number=service_number,
                confirmed=False
            ).update(confirmed=True)

            # Also forward to Node.js backend (best effort)
            try:
                requests.post(f'{NODE_BACKEND_URL}/api/medical/confirm', json=data, timeout=2)
            except:
                pass

            return JsonResponse({
                'message': f'{updated} medical entries confirmed successfully',
                'confirmed_count': updated
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_clear_medical_view(request, soldier_id):
    """Delete all medical entries for a soldier from Django DB."""
    if request.method == 'DELETE':
        try:
            deleted_count, _ = MedicalEntry.objects.filter(service_number=soldier_id).delete()
            return JsonResponse({
                'message': f'Cleared {deleted_count} medical entries for {soldier_id}',
                'deleted_count': deleted_count
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed — use DELETE'}, status=405)

def map_view(request):
    return render(request, 'map_view.html')
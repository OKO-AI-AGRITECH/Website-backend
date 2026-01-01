

from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import WaitlistSignup

@csrf_exempt
def join_waitlist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required_fields = [
        'full_name',
        'phone_number',
        'location',
        'farm_size'
    ]

    for field in required_fields:
        if not data.get(field):
            return JsonResponse({'error': f'{field} is required'}, status=400)

    WaitlistSignup.objects.create(
        full_name=data['full_name'],
        phone_number=data['phone_number'],
        location=data['location'],
        farm_size=data['farm_size'],
    )

    return JsonResponse({
        'success': True,
        'message': 'You have successfully joined the waitlist'
    }, status=201)

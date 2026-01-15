import json
import resend
import os
from django.conf import settings # Import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import WaitlistSignup

# Use the key from settings.py
resend.api_key = getattr(settings, 'RESEND_API_KEY', None)

@csrf_exempt
def join_waitlist(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    required_fields = ['full_name', 'email', 'phone_number', 'location', 'farm_size', 'farming_type']
    for field in required_fields:
        if not data.get(field):
            return JsonResponse({'error': f'The field "{field}" is required.'}, status=400)

    try:
        # 1. Save to Database
        new_signup = WaitlistSignup.objects.create(
            full_name=str(data['full_name']).strip(),
            email=str(data['email']).strip().lower(),
            phone_number=str(data['phone_number']).strip(),
            location=str(data['location']).strip(),
            farm_size=str(data['farm_size']).strip(),
            farming_type=data['farming_type'],
        )

        # 2. Send Email via Resend API
        if resend.api_key:
            try:
                params = {
                    # Pulls 'Oko <onboarding@resend.dev>' from settings
                    "from": settings.DEFAULT_FROM_EMAIL,
                    "to": [new_signup.email],
                    "subject": "Welcome to the Oko Waitlist!",
                    "html": f"""
                        <strong>Hi {new_signup.full_name},</strong>
                        <p>Thank you for joining the Oko waitlist! We are thrilled to have you.</p>
                        <p>We will keep you updated on our progress and notify you as soon as we launch.</p>
                    """
                }
                resend.Emails.send(params)
                print(f"--- SUCCESS: Email sent to {new_signup.email} via Resend ---")
            except Exception as e:
                print(f"--- RESEND ERROR: {e} ---")
        else:
            print("--- WARNING: RESEND_API_KEY not found in settings ---")

        return JsonResponse({
            'success': True,
            'message': 'Successfully joined the waitlist!'
        }, status=201)

    except IntegrityError:
        return JsonResponse({'error': 'This email is already registered.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
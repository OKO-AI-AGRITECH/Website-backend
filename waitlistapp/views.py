import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import WaitlistSignup
from django.db import IntegrityError # <--- IMPORTANT: Add this import

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
        # 1. Attempt to Save to Database
        new_signup = WaitlistSignup.objects.create(
            full_name=str(data['full_name']).strip(),
            email=str(data['email']).strip().lower(),
            phone_number=str(data['phone_number']).strip(),
            location=str(data['location']).strip(),
            farm_size=str(data['farm_size']).strip(),
            farming_type=data['farming_type'], 
        )

        # 2. Attempt to Send Email (Silent failure)
        try:
            send_mail(
                "Welcome to the Oko Waitlist!",
                f"Hi {new_signup.full_name}, thank you for joining!",
                settings.DEFAULT_FROM_EMAIL,
                [new_signup.email],
                fail_silently=True,
            )
        except:
            pass 

        # This returns a 201 status (GREEN in Postman)
        return JsonResponse({
            'success': True,
            'message': 'Successfully joined the waitlist!'
        }, status=201)

    except IntegrityError:
        # This catches the UNIQUE error and returns 400 (ORANGE in Postman)
        # Instead of crashing with a 500 error!
        return JsonResponse({
            'error': 'This email is already registered on our waitlist.'
        }, status=400)

    except Exception as e:
        # Catch-all for any other weird errors
        return JsonResponse({'error': str(e)}, status=500)

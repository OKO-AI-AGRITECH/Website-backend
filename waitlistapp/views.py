import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from .models import WaitlistSignup  
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

        # 2. Attempt to Send Email (Now with error logging!)
        try:
            send_mail(
                "Welcome to the Oko Waitlist!",
                f"Hi {new_signup.full_name}, thank you for joining!",
                settings.DEFAULT_FROM_EMAIL,
                [new_signup.email],
                fail_silently=False, # We set this to False so it triggers the "except" block on failure
            )
        except Exception as e:
            # This prints the error (like "Invalid login" or "Connection timeout") 
            # to your terminal so you can read it.
            print(f"--- EMAIL ERROR OCCURRED: {e} ---")

        return JsonResponse({
            'success': True,
            'message': 'Successfully joined the waitlist!'
        }, status=201)

    except IntegrityError:
        return JsonResponse({
            'error': 'This email is already registered on our waitlist.'
        }, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

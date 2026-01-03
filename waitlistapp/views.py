import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import WaitlistSignup
from django.db import IntegrityError # Added this to handle duplicates

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
        val = data.get(field)
        if val is None or val == "" or val == []:
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

        # 2. Send Automated Email
        subject = "Welcome to the Oko Waitlist!"
        message = f"Hi {new_signup.full_name},\n\nThank you for joining our waitlist! We've received your details for {new_signup.location}. We will be in touch soon.\n\nBest regards,\nThe Oko Team"
        
        # We use a try/except here so that if the email fails, 
        # the user still gets a "Success" message for the database part.
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [new_signup.email],
                fail_silently=True, 
            )
        except Exception:
            pass # Email failed, but we won't crash the whole request

        return JsonResponse({
            'success': True,
            'message': f'Success! You have been added to the waitlist.'
        }, status=201)

    except IntegrityError:
        # This catches the "Email already exists" error specifically
        return JsonResponse({'error': 'This email is already on our waitlist!'}, status=400)

    except Exception as e:
        # This catches anything else
        return JsonResponse({'error': 'An unexpected error occurred. Please try again.'}, status=500)

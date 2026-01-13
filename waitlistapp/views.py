import json
import yagmail
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
        # 1. Save to Database
        new_signup = WaitlistSignup.objects.create(
            full_name=str(data['full_name']).strip(),
            email=str(data['email']).strip().lower(),
            phone_number=str(data['phone_number']).strip(),
            location=str(data['location']).strip(),
            farm_size=str(data['farm_size']).strip(),
            farming_type=data['farming_type'], 
        )

        # 2. Send Email via yagmail
        try:
            # Initialize yagmail with credentials from Environment Variables
            yag = yagmail.SMTP(
                user=os.environ.get('EMAIL_USER'), 
                password=os.environ.get('EMAIL_PASSWORD')
            )

            # Define the email content
            subject = "Welcome to the Oko Waitlist!"
            contents = [
                f"Hi {new_signup.full_name},",
                "Thank you for joining the Oko waitlist! We are thrilled to have you.",
                "We will keep you updated on our progress and notify you as soon as we launch."
            ]

            # Send the email
            yag.send(
                to=new_signup.email,
                subject=subject,
                contents=contents
            )
            print(f"--- SUCCESS: Email sent to {new_signup.email} via yagmail ---")

        except Exception as e:
            # If email fails, we still return success for the signup but log the error
            print(f"--- YAGMAIL ERROR: {e} ---")

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
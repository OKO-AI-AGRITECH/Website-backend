import json
import resend
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import WaitlistSignup

# Initialize Resend with the API key from your settings.py
resend.api_key = getattr(settings, 'RESEND_API_KEY', None)

@csrf_exempt
def join_waitlist(request):
    """
    API Endpoint to handle waitlist signups and trigger a confirmation email.
    """
    # 1. Only allow POST requests
    if request.method != 'POST':
        return JsonResponse({
            'success': False, 
            'message': 'Method not allowed. Use POST.'
        }, status=405)

    # 2. Parse the JSON data from the request body
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'message': 'Invalid JSON format.'
        }, status=400)

    # 3. Define and validate required fields
    required_fields = ['full_name', 'email', 'phone_number', 'location', 'farm_size', 'farming_type']
    for field in required_fields:
        if not data.get(field):
            return JsonResponse({
                'success': False, 
                'message': f'The field "{field}" is required.'
            }, status=400)

    try:
        # 4. Save the user to the Database
        new_signup = WaitlistSignup.objects.create(
            full_name=str(data['full_name']).strip(),
            email=str(data['email']).strip().lower(),
            phone_number=str(data['phone_number']).strip(),
            location=str(data['location']).strip(),
            farm_size=str(data['farm_size']).strip(),
            farming_type=data['farming_type'],
        )

        # 5. Send Confirmation Email via Resend
        email_sent = False
        if resend.api_key:
            try:
                # IMPORTANT: Ensure settings.DEFAULT_FROM_EMAIL is 'onboarding@resend.dev' 
                # until your domain is verified.
                resend.emails.send({
                    "from": getattr(settings, 'DEFAULT_FROM_EMAIL', 'onboarding@resend.dev'),
                    "to": [new_signup.email],
                    "subject": "Welcome to the Oko Waitlist! 🚀",
                    "html": f"""
                        <div style="font-family: sans-serif; line-height: 1.5;">
                            <h2>Hi {new_signup.full_name},</h2>
                            <p>Thank you for joining the <strong>Oko</strong> waitlist!</p>
                            <p>We've recorded your interest in <strong>{new_signup.farming_type}</strong> farming in <strong>{new_signup.location}</strong>.</p>
                            <p>We will notify you as soon as we launch. Stay tuned!</p>
                            <br>
                            <p>Best regards,<br>The Oko Team</p>
                        </div>
                    """
                })
                email_sent = True
                print(f"--- SUCCESS: Email sent to {new_signup.email} ---")
            except Exception as e:
                # Log the error but don't stop the user from seeing a "Success" 
                # message because their data was saved to the DB.
                print(f"--- RESEND ERROR: {e} ---")
        else:
            print("--- WARNING: RESEND_API_KEY missing from settings ---")

        # 6. Return the Success JSON Response
        return JsonResponse({
            'success': True,
            'message': 'Successfully joined the waitlist!',
            'details': {
                'id': new_signup.id,
                'email_status': 'sent' if email_sent else 'failed_to_send'
            }
        }, status=201)

    except IntegrityError:
        # This handles the 'Unique' constraint if the email is already in the DB
        return JsonResponse({
            'success': False, 
            'message': 'This email is already registered on our waitlist.'
        }, status=400)
    
    except Exception as e:
        # General catch-all for server errors
        return JsonResponse({
            'success': False, 
            'message': f'Server error: {str(e)}'
        }, status=500)

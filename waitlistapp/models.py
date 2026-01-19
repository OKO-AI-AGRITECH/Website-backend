from django.db import models
from django.core.validators import RegexValidator

class WaitlistSignup(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    
    # This validator ensures the phone number is valid (e.g., +234...)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17) 
    
    location = models.CharField(max_length=255)
    farm_size = models.CharField(max_length=100)
    farming_type = models.JSONField(default=list) 
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.full_name} ({self.email})"

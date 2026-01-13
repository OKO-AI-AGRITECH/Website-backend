from django.db import models

class WaitlistSignup(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  # Added email field
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    farm_size = models.CharField(max_length=100)
    farming_type = models.JSONField(default=list) 
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.full_name} ({self.email})"
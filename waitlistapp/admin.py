from django.contrib import admin
from .models import WaitlistSignup

# This allows you to see the signups in the Django Admin panel
admin.site.register(WaitlistSignup)
from django.contrib import admin
from import_export.admin import ExportMixin
from .models import WaitlistSignup

@admin.register(WaitlistSignup)
class WaitlistSignupAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('full_name', 'email', 'location', 'display_farming', 'created_at')
    search_fields = ('full_name', 'email', 'location')
    list_filter = ('created_at',)

    def display_farming(self, obj):
        return ", ".join(obj.farming_type)
    display_farming.short_description = 'Farming Types'
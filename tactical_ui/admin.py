from django.contrib import admin
from .models import MedicalEntry


@admin.register(MedicalEntry)
class MedicalEntryAdmin(admin.ModelAdmin):
    list_display = ('service_number', 'injury', 'body_part', 'treatment', 'confirmed', 'timestamp')
    list_filter = ('service_number', 'confirmed', 'injury')
    search_fields = ('service_number', 'injury', 'body_part', 'treatment')
    ordering = ('-timestamp',)

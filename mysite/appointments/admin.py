from django.contrib import admin
from .models import Appointment, AppointmentSettings

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'ic_number', 'appointment_time', 'status', 'whatsapp_number', 'created_at')
    list_filter = ('status', 'appointment_time')
    search_fields = ('name', 'ic_number', 'whatsapp_number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'ic_number', 'whatsapp_number')
        }),
        ('Appointment Details', {
            'fields': ('appointment_time', 'status')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Appointment, AppointmentAdmin)

class AppointmentSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'slot_duration', 'max_appointments_per_slot')
    
    fieldsets = (
        ('Time Settings', {
            'fields': ('start_time', 'slot_duration')
        }),
        ('Capacity Settings', {
            'fields': ('max_appointments_per_slot',)
        }),
    )

admin.site.register(AppointmentSettings, AppointmentSettingsAdmin)

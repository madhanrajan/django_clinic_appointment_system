from django.db import models
from django.utils import timezone
import datetime

class AppointmentSettings(models.Model):
    """Settings for appointment system configuration"""
    start_time = models.TimeField(default=timezone.now)
    slot_duration = models.IntegerField(default=15, help_text="Duration of each appointment slot in minutes")
    max_appointments_per_slot = models.IntegerField(default=1, help_text="Maximum number of appointments allowed per time slot")
    
    @classmethod
    def get_settings(cls):
        """Get or create settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    name = models.CharField(max_length=100)
    ic_number = models.CharField(max_length=20, unique=True)
    appointment_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.appointment_time.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def get_next_available_slot(cls, start_time=None, duration_minutes=None):
        """
        Find the next available appointment slot
        
        Args:
            start_time: Optional datetime to start from. If None, uses current time.
            duration_minutes: The duration of each appointment slot in minutes. If None, uses the value from settings.
        
        Returns:
            The next available appointment time as a datetime object.
        """
        # Get settings
        settings = AppointmentSettings.get_settings()
        
        # Use provided duration or get from settings
        if duration_minutes is None:
            duration_minutes = settings.slot_duration
        
        # Use provided start time or current time
        base_time = start_time if start_time else timezone.now()
        
        # Round up to the next interval
        minutes = (base_time.minute // duration_minutes + 1) * duration_minutes
        next_slot = base_time.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=minutes)
        
        # Check if this slot is already at capacity
        max_per_slot = settings.max_appointments_per_slot
        
        while True:
            # Count appointments in this slot
            count = cls.objects.filter(
                appointment_time=next_slot, 
                status__in=['PENDING', 'CONFIRMED']
            ).count()
            
            # If slot has space, return it
            if count < max_per_slot:
                return next_slot
                
            # Otherwise, move to next slot
            next_slot += datetime.timedelta(minutes=duration_minutes)
    
    @classmethod
    def is_slot_available(cls, time_slot):
        """
        Check if a specific time slot is available
        
        Args:
            time_slot: The datetime to check
        
        Returns:
            Boolean indicating if the slot is available
        """
        settings = AppointmentSettings.get_settings()
        
        # Count appointments in this slot
        count = cls.objects.filter(
            appointment_time=time_slot, 
            status__in=['PENDING', 'CONFIRMED']
        ).count()
        
        # Return True if slot has space
        return count < settings.max_appointments_per_slot

from django.core.management.base import BaseCommand
from appointments.models import AppointmentSettings

class Command(BaseCommand):
    help = 'Initialize appointment settings'

    def handle(self, *args, **options):
        # Check if settings already exist
        if AppointmentSettings.objects.exists():
            self.stdout.write(self.style.WARNING('Settings already exist. No changes made.'))
            return
        
        # Create default settings
        settings = AppointmentSettings.objects.create(
            start_time='09:00',
            slot_duration=15,
            max_appointments_per_slot=1
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created appointment settings: {settings}'))

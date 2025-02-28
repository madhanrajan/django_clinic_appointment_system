from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Appointment, AppointmentSettings

class AppointmentSettingsForm(forms.ModelForm):
    """Form for configuring appointment settings"""
    class Meta:
        model = AppointmentSettings
        fields = ['start_time', 'slot_duration', 'max_appointments_per_slot']
        widgets = {
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'slot_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '5', 'max': '60'}),
            'max_appointments_per_slot': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
        }

class AppointmentForm(forms.ModelForm):
    TIME_CHOICES = [
        ('auto', 'Set automatically (next available slot)'),
        ('manual', 'Select a specific time'),
    ]
    
    time_selection = forms.ChoiceField(
        choices=TIME_CHOICES, 
        initial='auto',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    custom_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'id': 'custom_time'
            }
        )
    )
    
    def clean_custom_time(self):
        """Validate that the selected time slot is available"""
        time_selection = self.cleaned_data.get('time_selection')
        custom_time = self.cleaned_data.get('custom_time')
        
        if time_selection == 'manual' and custom_time:
            # Round to nearest slot interval
            settings = AppointmentSettings.get_settings()
            duration = settings.slot_duration
            minutes = (custom_time.minute // duration) * duration
            rounded_time = custom_time.replace(minute=minutes, second=0, microsecond=0)
            
            # Check if slot is available
            if not Appointment.is_slot_available(rounded_time):
                raise ValidationError("This time slot is already fully booked. Please select another time.")
            
            return rounded_time
        
        return custom_time
    
    class Meta:
        model = Appointment
        fields = ['name', 'ic_number', 'whatsapp_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'ic_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your IC number'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your WhatsApp number (with country code)'}),
        }

class AdminAppointmentForm(forms.ModelForm):
    """Form for administrators to create and edit appointments"""
    
    class Meta:
        model = Appointment
        fields = ['name', 'ic_number', 'appointment_time', 'status', 'whatsapp_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'ic_number': forms.TextInput(attrs={'class': 'form-control'}),
            'appointment_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.instance_id = None
        if 'instance' in kwargs and kwargs['instance']:
            self.instance_id = kwargs['instance'].id
        super().__init__(*args, **kwargs)
        
    def clean_ic_number(self):
        ic_number = self.cleaned_data.get('ic_number')
        # Remove any spaces or dashes
        ic_number = ic_number.replace(' ', '').replace('-', '')
        
        # Check for uniqueness, but exclude the current instance
        if self.instance_id:
            if Appointment.objects.filter(ic_number=ic_number).exclude(id=self.instance_id).exists():
                raise ValidationError("This IC number is already in use.")
        else:
            if Appointment.objects.filter(ic_number=ic_number).exists():
                raise ValidationError("This IC number is already in use.")
                
        return ic_number
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
        
    def clean_whatsapp_number(self):
        whatsapp_number = self.cleaned_data.get('whatsapp_number')
        if whatsapp_number:
            # Ensure the number starts with +
            if not whatsapp_number.startswith('+'):
                whatsapp_number = '+' + whatsapp_number
            # Remove any spaces or dashes
            whatsapp_number = whatsapp_number.replace(' ', '').replace('-', '')
        return whatsapp_number

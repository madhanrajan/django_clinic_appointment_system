from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.conf import settings
from django.urls import reverse
from django.db.models import Count
from .models import Appointment, AppointmentSettings
from .forms import AppointmentForm, AdminAppointmentForm, AppointmentSettingsForm
from .utils import send_whatsapp_message, generate_appointment_message

# Helper function to check if user is admin
def is_admin(user):
    return user.is_staff or user.is_superuser

# Admin Views
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminSettingsView(View):
    """View for managing appointment settings"""
    def get(self, request):
        settings = AppointmentSettings.get_settings()
        form = AppointmentSettingsForm(instance=settings)
        return render(request, 'appointments/admin_settings.html', {
            'form': form,
            'settings': settings
        })
    
    def post(self, request):
        settings = AppointmentSettings.get_settings()
        form = AppointmentSettingsForm(request.POST, instance=settings)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated successfully.")
            return redirect('admin_settings')
        
        return render(request, 'appointments/admin_settings.html', {
            'form': form,
            'settings': settings
        })

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        # Get all appointments
        appointments = Appointment.objects.all().order_by('-appointment_time')
        
        # Get counts for dashboard stats
        total_appointments = appointments.count()
        confirmed_appointments = appointments.filter(status='CONFIRMED').count()
        pending_appointments = appointments.filter(status='PENDING').count()
        cancelled_appointments = appointments.filter(status='CANCELLED').count()
        
        # Get appointment settings
        settings = AppointmentSettings.get_settings()
        
        context = {
            'appointments': appointments,
            'total_appointments': total_appointments,
            'confirmed_appointments': confirmed_appointments,
            'pending_appointments': pending_appointments,
            'cancelled_appointments': cancelled_appointments,
            'settings': settings,
        }
        
        return render(request, 'appointments/admin_dashboard.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminAppointmentDetailView(View):
    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        settings = AppointmentSettings.get_settings()
        return render(request, 'appointments/admin_appointment_detail.html', {
            'appointment': appointment,
            'settings': settings
        })

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminAppointmentEditView(View):
    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        form = AdminAppointmentForm(instance=appointment)
        settings = AppointmentSettings.get_settings()
        return render(request, 'appointments/admin_appointment_form.html', {
            'form': form,
            'appointment': appointment,
            'settings': settings,
            'is_edit': True
        })
    
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        form = AdminAppointmentForm(request.POST, instance=appointment)
        settings = AppointmentSettings.get_settings()
        
        if form.is_valid():
            appointment = form.save()
            
            # Send notification if status changed
            if 'status' in form.changed_data:
                message = generate_appointment_message(appointment, is_update=True, status_change=True)
                if appointment.whatsapp_number:
                    send_whatsapp_message(appointment.whatsapp_number, message)
            
            messages.success(request, "Appointment updated successfully.")
            return redirect('admin_dashboard')
        
        return render(request, 'appointments/admin_appointment_form.html', {
            'form': form,
            'appointment': appointment,
            'settings': settings,
            'is_edit': True
        })

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminAppointmentCreateView(View):
    def get(self, request):
        form = AdminAppointmentForm()
        settings = AppointmentSettings.get_settings()
        return render(request, 'appointments/admin_appointment_form.html', {
            'form': form,
            'settings': settings,
            'is_edit': False
        })
    
    def post(self, request):
        form = AdminAppointmentForm(request.POST)
        settings = AppointmentSettings.get_settings()
        
        if form.is_valid():
            appointment = form.save()
            
            # Send notification
            message = generate_appointment_message(appointment)
            if appointment.whatsapp_number:
                send_whatsapp_message(appointment.whatsapp_number, message)
            
            messages.success(request, "Appointment created successfully.")
            return redirect('admin_dashboard')
        
        return render(request, 'appointments/admin_appointment_form.html', {
            'form': form,
            'settings': settings,
            'is_edit': False
        })

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminAppointmentDeleteView(View):
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        
        # Store name for message
        name = appointment.name
        
        # Delete the appointment
        appointment.delete()
        
        messages.success(request, f"Appointment for {name} deleted successfully.")
        return redirect('admin_dashboard')

def landing_view(request):
    return render(request, 'appointments/landing.html')

def test_view(request):
    return render(request, 'appointments/test.html')

class AppointmentFormView(View):
    def get(self, request):
        form = AppointmentForm()
        settings = AppointmentSettings.get_settings()
        return render(request, 'appointments/appointment_form.html', {
            'form': form,
            'settings': settings
        })
    
    def post(self, request):
        form = AppointmentForm(request.POST)
        settings = AppointmentSettings.get_settings()
        
        if form.is_valid():
            # Don't save the form yet, just get an instance
            appointment = form.save(commit=False)
            
            # Check time selection mode
            time_selection = form.cleaned_data.get('time_selection')
            
            if time_selection == 'auto':
                # Get the next available slot based on current time
                next_slot = Appointment.get_next_available_slot()
                appointment.appointment_time = next_slot
            else:  # 'manual'
                # Get the user-selected time (already validated in form clean method)
                custom_time = form.cleaned_data.get('custom_time')
                appointment.appointment_time = custom_time
            
            # Save the appointment
            appointment.save()
            
            # Generate appointment message using ChatGPT
            message = generate_appointment_message(appointment)
            
            # Send WhatsApp message if number is provided
            if appointment.whatsapp_number:
                send_whatsapp_message(appointment.whatsapp_number, message)
                
            # Redirect to confirmation page
            return redirect(reverse('appointment_confirmation', kwargs={'pk': appointment.pk}))
        
        return render(request, 'appointments/appointment_form.html', {
            'form': form,
            'settings': settings
        })

class AppointmentConfirmationView(View):
    def get(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
            return render(request, 'appointments/appointment_confirmation.html', {'appointment': appointment})
        except Appointment.DoesNotExist:
            messages.error(request, "Appointment not found.")
            return redirect('appointment_form')

class AppointmentAdjustView(View):
    def get(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
            return render(request, 'appointments/appointment_adjust.html', {'appointment': appointment})
        except Appointment.DoesNotExist:
            messages.error(request, "Appointment not found.")
            return redirect('appointment_form')
    
    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
            
            # Get the new time from the request
            new_time_str = request.POST.get('new_time')
            if new_time_str:
                from datetime import datetime
                # Parse the new time
                try:
                    # Try the standard format first
                    new_time = datetime.strptime(new_time_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    try:
                        # Try alternative format
                        new_time = datetime.strptime(new_time_str, '%Y-%m-%d %H:%M')
                    except ValueError:
                        # If all else fails, log the format and raise an error
                        print(f"Received time format: {new_time_str}")
                        messages.error(request, f"Invalid time format: {new_time_str}")
                        return render(request, 'appointments/appointment_adjust.html', {'appointment': appointment})
                
                # Update the appointment
                appointment.appointment_time = new_time
                appointment.save()
                
                # Generate new appointment message
                message = generate_appointment_message(appointment, is_update=True)
                
                # Send WhatsApp message if number is provided
                if appointment.whatsapp_number:
                    send_whatsapp_message(appointment.whatsapp_number, message)
                
                messages.success(request, "Appointment time updated successfully.")
                return redirect(reverse('appointment_confirmation', kwargs={'pk': appointment.pk}))
            
            messages.error(request, "Please select a valid time.")
            return render(request, 'appointments/appointment_adjust.html', {'appointment': appointment})
            
        except Appointment.DoesNotExist:
            messages.error(request, "Appointment not found.")
            return redirect('appointment_form')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Appointment
from .utils import send_whatsapp_message, generate_appointment_message

@method_decorator(csrf_exempt, name='dispatch')
class AppointmentAPIView(View):
    """API endpoint for creating appointments from WhatsApp"""
    
    def get(self, request):
        """List all appointments"""
        appointments = Appointment.objects.all().order_by('-appointment_time')
        data = []
        
        for appointment in appointments:
            data.append({
                'id': appointment.id,
                'name': appointment.name,
                'ic_number': appointment.ic_number,
                'appointment_time': appointment.appointment_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': appointment.status,
                'whatsapp_number': appointment.whatsapp_number,
                'created_at': appointment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': appointment.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return JsonResponse({'appointments': data})
    
    def post(self, request):
        """Create a new appointment"""
        try:
            # Parse JSON data
            data = json.loads(request.body)
            
            # Extract data
            name = data.get('name')
            ic_number = data.get('ic_number')
            whatsapp_number = data.get('whatsapp_number')
            
            # Validate required fields
            if not name or not ic_number:
                return JsonResponse({
                    'success': False,
                    'message': 'Name and IC number are required'
                }, status=400)
            
            # Check if an appointment with this IC number already exists
            existing_appointment = Appointment.objects.filter(ic_number=ic_number).first()
            if existing_appointment:
                # Return existing appointment info
                return JsonResponse({
                    'success': True,
                    'message': f"You already have an appointment scheduled for {existing_appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}. If you need to reschedule, please contact our clinic."
                })
            
            # Get next available appointment slot
            next_slot = Appointment.get_next_available_slot()
            
            # Create new appointment
            appointment = Appointment.objects.create(
                name=name,
                ic_number=ic_number,
                appointment_time=next_slot,
                status='CONFIRMED',
                whatsapp_number=whatsapp_number
            )
            
            # Generate confirmation message
            confirmation_message = generate_appointment_message(appointment)
            
            return JsonResponse({
                'success': True,
                'appointment_id': appointment.id,
                'appointment_time': appointment.appointment_time.strftime('%Y-%m-%d %H:%M:%S'),
                'message': confirmation_message
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"An error occurred: {str(e)}"
            }, status=500)
    
    def put(self, request, appointment_id):
        """Update an existing appointment"""
        try:
            # Get appointment
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Parse JSON data
            data = json.loads(request.body)
            
            # Update fields
            if 'name' in data:
                appointment.name = data['name']
            if 'ic_number' in data:
                appointment.ic_number = data['ic_number']
            if 'status' in data:
                appointment.status = data['status']
            if 'whatsapp_number' in data:
                appointment.whatsapp_number = data['whatsapp_number']
            
            # Save changes
            appointment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Appointment updated successfully'
            })
            
        except Appointment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Appointment not found'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"An error occurred: {str(e)}"
            }, status=500)
    
    def delete(self, request, appointment_id):
        """Delete an appointment"""
        try:
            # Get appointment
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Delete appointment
            appointment.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Appointment deleted successfully'
            })
            
        except Appointment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Appointment not found'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"An error occurred: {str(e)}"
            }, status=500) 
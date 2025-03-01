from django.urls import path
from .api import AppointmentAPIView

urlpatterns = [
    path('', AppointmentAPIView.as_view(), name='api_appointments'),
    path('<int:appointment_id>/', AppointmentAPIView.as_view(), name='api_appointment_detail'),
] 
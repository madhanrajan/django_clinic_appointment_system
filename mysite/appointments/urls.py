from django.urls import path
from . import views

# User-facing URLs
urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('book/', views.AppointmentFormView.as_view(), name='appointment_form'),
    path('confirmation/<int:pk>/', views.AppointmentConfirmationView.as_view(), name='appointment_confirmation'),
    path('adjust/<int:pk>/', views.AppointmentAdjustView.as_view(), name='appointment_adjust'),
    path('test/', views.test_view, name='test_view'),
    
    # Admin URLs
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/settings/', views.AdminSettingsView.as_view(), name='admin_settings'),
    path('admin/appointment/<int:pk>/', views.AdminAppointmentDetailView.as_view(), name='admin_appointment_detail'),
    path('admin/appointment/<int:pk>/edit/', views.AdminAppointmentEditView.as_view(), name='admin_appointment_edit'),
    path('admin/appointment/create/', views.AdminAppointmentCreateView.as_view(), name='admin_appointment_create'),
    path('admin/appointment/<int:pk>/delete/', views.AdminAppointmentDeleteView.as_view(), name='admin_appointment_delete'),
]

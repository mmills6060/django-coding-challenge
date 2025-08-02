from django.urls import path
from . import views

app_name = 'payloads'

urlpatterns = [
    # Main payload reception endpoint
    path('receive/', views.receive_payload, name='receive_payload'),
    
    # Device endpoints
    path('devices/', views.DeviceListView.as_view(), name='device_list'),
    path('devices/<str:devEUI>/', views.DeviceDetailView.as_view(), name='device_detail'),
    path('devices/<str:devEUI>/payloads/', views.device_payloads, name='device_payloads'),
    
    # Payload endpoints
    path('payloads/', views.PayloadListView.as_view(), name='payload_list'),
    path('payloads/<int:pk>/', views.PayloadDetailView.as_view(), name='payload_detail'),
] 
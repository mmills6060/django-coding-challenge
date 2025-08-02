from django.contrib import admin
from .models import Device, Payload


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['devEUI', 'latest_status', 'created_at', 'updated_at']
    list_filter = ['latest_status', 'created_at', 'updated_at']
    search_fields = ['devEUI']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']


@admin.register(Payload)
class PayloadAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'fCnt', 'data_hex', 'is_passing', 'created_at']
    list_filter = ['is_passing', 'created_at', 'device']
    search_fields = ['device__devEUI', 'fCnt']
    readonly_fields = ['data_hex', 'is_passing', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('device')

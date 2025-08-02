from rest_framework import serializers
from .models import Device, Payload


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'devEUI', 'latest_status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'latest_status', 'created_at', 'updated_at']


class PayloadSerializer(serializers.ModelSerializer):
    device_devEUI = serializers.CharField(write_only=True, source='device.devEUI')
    
    class Meta:
        model = Payload
        fields = [
            'id', 'device', 'device_devEUI', 'fCnt', 'data', 'data_hex', 
            'is_passing', 'rx_info', 'tx_info', 'created_at'
        ]
        read_only_fields = ['id', 'device', 'data_hex', 'is_passing', 'created_at']

    def validate(self, data):
        """
        Validate the payload data and ensure no duplicate fCnt for the same device.
        """
        devEUI = data.get('device', {}).get('devEUI')
        fCnt = data.get('fCnt')
        
        if not devEUI:
            raise serializers.ValidationError("devEUI is required")
        
        if not fCnt:
            raise serializers.ValidationError("fCnt is required")
        
        # Check if this fCnt already exists for this device
        try:
            device = Device.objects.get(devEUI=devEUI)
            if Payload.objects.filter(device=device, fCnt=fCnt).exists():
                raise serializers.ValidationError(
                    f"Payload with fCnt {fCnt} already exists for device {devEUI}"
                )
        except Device.DoesNotExist:
            # Device doesn't exist, we'll create it
            pass
        
        return data

    def create(self, validated_data):
        """
        Create or get the device and create the payload.
        """
        devEUI = validated_data.pop('device')['devEUI']
        
        # Get or create the device
        device, created = Device.objects.get_or_create(devEUI=devEUI)
        
        # Create the payload
        payload = Payload.objects.create(device=device, **validated_data)
        
        return payload


class IoTPayloadSerializer(serializers.Serializer):
    """
    Serializer for incoming IoT payload format.
    """
    fCnt = serializers.IntegerField()
    devEUI = serializers.CharField(max_length=16)
    data = serializers.CharField()
    rxInfo = serializers.ListField(default=list)
    txInfo = serializers.DictField(default=dict)

    def validate_data(self, value):
        """
        Validate that the data field is valid Base64.
        """
        import base64
        try:
            base64.b64decode(value)
            return value
        except Exception:
            raise serializers.ValidationError("Invalid Base64 data")

    def create(self, validated_data):
        """
        Convert the IoT payload format to our internal format and save.
        """
        # Map the IoT payload format to our internal format
        payload_data = {
            'fCnt': validated_data['fCnt'],
            'data': validated_data['data'],
            'rx_info': validated_data['rxInfo'],
            'tx_info': validated_data['txInfo'],
            'device_devEUI': validated_data['devEUI']
        }
        
        # Use the PayloadSerializer to create the payload
        payload_serializer = PayloadSerializer(data=payload_data)
        payload_serializer.is_valid(raise_exception=True)
        return payload_serializer.save() 
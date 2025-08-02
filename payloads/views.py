from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Device, Payload
from .serializers import DeviceSerializer, PayloadSerializer, IoTPayloadSerializer


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def receive_payload(request):
    """
    Receive and process IoT device payloads.
    
    Expected payload format:
    {
        "fCnt": 100,
        "devEUI": "abcdabcdabcdabcd",
        "data": "AQ==",
        "rxInfo": [...],
        "txInfo": {...}
    }
    """
    try:
        serializer = IoTPayloadSerializer(data=request.data)
        if serializer.is_valid():
            payload = serializer.save()
            
            # Return the created payload with device information
            response_serializer = PayloadSerializer(payload)
            return Response({
                'message': 'Payload received and processed successfully',
                'payload': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Invalid payload data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': 'Failed to process payload',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceListView(generics.ListAPIView):
    """
    List all devices with their latest status.
    """
    queryset = Device.objects.all().order_by('-updated_at')
    serializer_class = DeviceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class DeviceDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific device.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'devEUI'


class PayloadListView(generics.ListAPIView):
    """
    List all payloads with optional filtering by device.
    """
    serializer_class = PayloadSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Payload.objects.all().select_related('device').order_by('-created_at')
        devEUI = self.request.query_params.get('devEUI', None)
        if devEUI:
            queryset = queryset.filter(device__devEUI=devEUI)
        return queryset


class PayloadDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific payload.
    """
    queryset = Payload.objects.all().select_related('device')
    serializer_class = PayloadSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def device_payloads(request, devEUI):
    """
    Get all payloads for a specific device.
    """
    try:
        device = get_object_or_404(Device, devEUI=devEUI)
        payloads = Payload.objects.filter(device=device).order_by('-created_at')
        serializer = PayloadSerializer(payloads, many=True)
        
        return Response({
            'device': DeviceSerializer(device).data,
            'payloads': serializer.data,
            'total_payloads': payloads.count()
        })
        
    except Device.DoesNotExist:
        return Response({
            'error': f'Device with devEUI {devEUI} not found'
        }, status=status.HTTP_404_NOT_FOUND)

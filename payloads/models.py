from django.db import models
import base64


class Device(models.Model):
    """
    Model to store IoT device information.
    """
    devEUI = models.CharField(max_length=16, unique=True, help_text="Device EUI identifier")
    latest_status = models.BooleanField(default=False, help_text="Latest payload status (True=passing, False=failing)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Device {self.devEUI}"

    class Meta:
        db_table = 'devices'


class Payload(models.Model):
    """
    Model to store IoT device payloads.
    """
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='payloads')
    fCnt = models.IntegerField(help_text="Frame counter to prevent duplicate messages")
    data = models.TextField(help_text="Base64 encoded data")
    data_hex = models.CharField(max_length=255, blank=True, help_text="Hexadecimal representation of decoded data")
    is_passing = models.BooleanField(default=False, help_text="Whether the payload indicates passing status")
    rx_info = models.JSONField(default=list, help_text="Receive information from gateways")
    tx_info = models.JSONField(default=dict, help_text="Transmit information")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payload {self.fCnt} from {self.device.devEUI}"

    def save(self, *args, **kwargs):
        # Decode Base64 data to hexadecimal
        try:
            decoded_bytes = base64.b64decode(self.data)
            self.data_hex = decoded_bytes.hex()
            
            # Check if the decoded value is 1 (passing) or anything else (failing)
            if decoded_bytes == b'\x01':
                self.is_passing = True
            else:
                self.is_passing = False
        except Exception as e:
            # If decoding fails, mark as failing
            self.data_hex = ""
            self.is_passing = False
        
        super().save(*args, **kwargs)
        
        # Update device's latest status
        self.device.latest_status = self.is_passing
        self.device.save()

    class Meta:
        db_table = 'payloads'
        unique_together = ['device', 'fCnt']  # Prevent duplicate fCnt for same device

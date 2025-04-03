# order/payment_utils.py
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings


def generate_paynow_qr(order, amount):
    # In a real implementation, you would generate a proper PayNow QR code
    # This is just a placeholder implementation
    qr = qrcode.make(f"PAYNOW|{order.id}|{amount}")
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())

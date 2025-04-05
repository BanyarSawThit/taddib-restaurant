from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_payment_confirmation(order, payment, email=None):
    """Send email confirmation for successful payment"""
    subject = f"TADDIB - Order #{order.id} Confirmation"
    context = {
        'order': order,
        'payment': payment,
        'restaurant_name': 'TADDIB'
    }

    # Render HTML email template
    html_message = render_to_string('order/email/confirmation.html', context)
    plain_message = strip_tags(html_message)

    # Determine recipient email
    recipient = email or payment.billing_email or getattr(order, 'customer_email', None)
    if not recipient:
        return False

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


# email_utils.py

def send_sms_confirmation(order, phone_number):
    """Send SMS via carrier email gateway"""
    if not phone_number or not getattr(settings, 'SMS_ENABLED', False):
        return False

    try:
        # Remove any non-digit characters from phone number
        phone_number = ''.join(filter(str.isdigit, phone_number))

        # For Singtel Singapore numbers (starting with 8 or 9)
        if phone_number.startswith('65'):
            phone_number = phone_number[2:]  # Remove country code
        if phone_number.startswith('8') or phone_number.startswith('9'):
            recipient = f"{phone_number}@singtel.com"
        else:
            return False

        subject = ""
        message = f"TADDIB: Order #{order.id} confirmed. Total: ${order.get_total()}"

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        return False
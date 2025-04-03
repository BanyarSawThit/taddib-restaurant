from django.shortcuts import render, get_object_or_404, redirect

from .email_utils import send_sms_confirmation
from .models import Table, Category, Item, Selection, Order, OrderItem, MeatOption, SpicyLevel, Payment
from .forms import SelectionForm
from django.contrib import messages
import stripe
from django.conf import settings
from django.http import JsonResponse
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import time
import random
import json
from .payment_utils import generate_paynow_qr
from django.http import JsonResponse
from decimal import Decimal
from django.core.files.base import ContentFile
from django.urls import reverse

# order/views.py
stripe.api_key = settings.STRIPE_SECRET_KEY


def payment_checkout(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if not settings.STRIPE_PUBLIC_KEY or not settings.STRIPE_SECRET_KEY:
        messages.error(request, "Payment system is currently unavailable. Please try again later.")
        return redirect('table_view')

    # For PayNow, generate QR code if enabled
    qr_code = None
    if getattr(settings, 'ENABLE_PAYNOW', False):
        try:
            qr_img = qrcode.make(f"PAYNOW|{order.id}|{order.get_total()}")
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            qr_code = base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            print(f"Error generating QR code: {e}")

    return render(request, 'order/payment/payment_options.html', {
        'order': order,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
        'qr_code': qr_code,
        'enable_paynow': getattr(settings, 'ENABLE_PAYNOW', False)
    })


def process_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                payment_type = data.get('payment_type')
                phone_number = data.get('phone_number')  # Get phone number for SMS
            else:
                payment_type = request.POST.get('payment_type')
                phone_number = request.POST.get('phone_number')  # Get phone number for SMS

            if payment_type == 'card':
                # Process Stripe payment
                payment_method_id = data.get('payment_method_id')

                # Create and confirm the payment intent
                intent = stripe.PaymentIntent.create(
                    amount=int(order.get_total() * 100),  # Amount in cents
                    socurrency=settings.STRIPE_CURRENCY,
                    payment_method=payment_method_id,
                    confirmation_method='manual',
                    confirm=True,
                    description=f'Order #{order.id}',
                    metadata={
                        'order_id': order.id,
                        'phone_number': phone_number  # Store phone number in metadata
                    },
                    receipt_email=data.get('email')  # Add email for receipt if available
                )

                # Check if payment requires additional action (3D Secure)
                if intent.status == 'requires_action':
                    return JsonResponse({
                        'requires_action': True,
                        'payment_intent_client_secret': intent.client_secret
                    })
                elif intent.status == 'succeeded':
                    # Create payment record
                    payment = Payment.objects.create(
                        order=order,
                        amount=order.get_total(),
                        stripe_charge_id=intent.id,
                        status='completed',
                        payment_method='card',
                        customer_phone=phone_number  # Store customer phone number
                    )

                    order.status = 'Completed'
                    order.save()

                    # Send SMS confirmation
                    if phone_number:
                        send_sms_confirmation(order, phone_number)

                    return JsonResponse(
                        {'success': True, 'redirect_url': reverse('payment_confirmation', args=[order.id])})
                else:
                    raise Exception(f"Payment failed with status: {intent.status}")

            elif payment_type == 'cash':
                # Process cash payment
                payment = Payment.objects.create(
                    order=order,
                    amount=order.get_total(),
                    status='pending',
                    payment_method='cash',
                    customer_phone=phone_number or None # Store customer phone number
                )
                order.status = 'Pending Payment'
                order.save()

                messages.success(request, "Cash payment received! Please present this receipt to staff.")

                # Add success message
                messages.success(request, f"Cash payment recorded for order #{order.id}")

                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('cash_receipt', args=[order.id])
                })

            elif payment_type == 'paynow':
                # Process PayNow payment
                payment = Payment.objects.create(
                    order=order,
                    amount=order.get_total(),
                    status='pending',
                    payment_method='paynow',
                    customer_phone='90535597'  # Your PayNow number
                )
                order.status = 'Pending Payment'
                order.save()

                # Generate QR code
                qr_img = qrcode.make(f"PAYNOW|{order.id}|{order.get_total()}")
                buffer = BytesIO()
                qr_img.save(buffer, format="PNG")

                payment.qr_code.save(f'paynow_{order.id}.png', ContentFile(buffer.getvalue()))
                payment.save()

                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('payment_confirmation', args=[order.id])
                })

        except stripe.error.CardError as e:
            return JsonResponse({'error': e.user_message}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def payment_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    payment = get_object_or_404(Payment, order=order)
    return render(request, 'order/payment/confirmation.html', {
        'order': order,
        'payment': payment
    })


def payment_error(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order/payment/error.html', {'order': order})


def cash_receipt(request, order_id):
    """View to display the cash payment receipt"""
    order = get_object_or_404(Order, pk=order_id)
    payment = get_object_or_404(Payment, order=order, payment_method='cash')
    return render(request, 'order/payment/cash_receipt.html', {
        'order': order,
        'payment': payment
    })


# Render the table selection page
def table_view(request):
    tables = Table.objects.all()
    return render(request, 'order/table_page.html', {'tables': tables})


def menu_view(request, table_id):
    table = get_object_or_404(Table, pk=table_id)
    categories = Category.objects.all()
    menu_items = Item.objects.all()
    return render(request, 'order/menu_page.html', {
        'menu_items': menu_items,
        'categories': categories,
        'table': table,
        'table_id': table_id,
    })


def selection_view(request, table_id, item_id):
    """
    Renders the selection page for a given item and table
    Passes available spicy levels if the item supports spicy options
    """
    form = SelectionForm()
    item = get_object_or_404(Item, pk=item_id)
    table = get_object_or_404(Table, pk=table_id)
    spicylevels = SpicyLevel.objects.all() if item.has_spicy_options else None

    if request.method == 'POST':

        post_data = request.POST.copy()
        if post_data.get('meat_option') == "":
            post_data['meat_option'] = None

        if post_data.get('spicy_level') == "":
            post_data['spicy_level'] = None

        form = SelectionForm(post_data)

        if form.is_valid():
            selection = form.save(commit=False)
            selection.item = item
            selection.save()

            messages.success(request, "Item successfully added to cart!")

            return render(request, 'cart/cart_summary.html')
        else:
            # If the form is not valid, create a new empty form instance (or re-render with errors).
            messages.error(request, "There was an error with your selection. Please try again.")
            form = SelectionForm()

    return render(request, 'order/selection_page.html',
                  {'item': item,
                   'form': form,
                   'table_id': table_id,
                   'spicylevels': spicylevels,
                   })

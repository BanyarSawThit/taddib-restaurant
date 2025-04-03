# order/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment


@receiver(post_save, sender=Payment)
def update_order_status(sender, instance, created, **kwargs):
    """Update order status when payment is completed"""
    if created and instance.status == 'completed':
        instance.order.status = 'Completed'
        instance.order.save()

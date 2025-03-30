from django.shortcuts import render, get_object_or_404, redirect
from order.models import Order, OrderItem
from django.utils import timezone

def bar_dashboard(request):
    # Get all pending orders with drink items
    pending_orders = Order.objects.filter(
        status='Pending'
    ).prefetch_related('order_items').order_by('date_ordered')

    # Count waiting drink orders
    waiting_count = pending_orders.filter(bar_status='Waiting').count()

    context = {
        'pending_orders': pending_orders,
        'waiting_count': waiting_count,
    }
    return render(request, 'bar/dashboard.html', context)

def mark_drinks_ready(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.bar_status != 'Ready':  # Prevent marking already ready orders
        order.bar_status = 'Ready'
        order.save()
    return redirect('bar:dashboard')

def drink_history(request):
    # Get completed orders (both served and completed)
    completed_orders = Order.objects.exclude(
        status='Pending'
    ).order_by('-date_ordered')

    context = {
        'completed_orders': completed_orders,
    }
    return render(request, 'bar/history.html', context)
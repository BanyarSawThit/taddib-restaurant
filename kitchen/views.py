from django.shortcuts import render, get_object_or_404, redirect
from order.models import Order

def kitchen_view(request):
    # Get all pending orders with kitchen items that are waiting
    waiting_orders = Order.objects.filter(
        status='Pending',
        kitchen_status='Waiting'
    ).prefetch_related('order_items').order_by('date_ordered')[:6]  # Limit to 6 orders

    # Get preparing orders (for potential display if needed)
    preparing_orders = Order.objects.filter(
        status='Pending',
        kitchen_status='Preparing'
    ).prefetch_related('order_items').order_by('date_ordered')

    # Count waiting orders
    waiting_count = Order.objects.filter(
        status='Pending',
        kitchen_status='Waiting'
    ).count()

    context = {
        'waiting_orders': waiting_orders,
        'preparing_orders': preparing_orders,
        'waiting_count': waiting_count,
    }

    return render(request, 'kitchen/dashboard.html', context)


def history_view(request):
    # Get completed orders (both served and completed)
    completed_orders = Order.objects.exclude(
        status='Pending',
        kitchen_status='Waiting'
    ).order_by('-date_ordered')

    context = {
        'completed_orders': completed_orders,
    }
    return render(request, 'kitchen/history.html', context)


def mark_order_ready(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.kitchen_status = 'Ready'
        order.save()
    return redirect('kitchen:kitchen_view')
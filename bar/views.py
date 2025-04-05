from django.shortcuts import render, get_object_or_404, redirect
from order.models import Order

def bar_view(request):
    # Get all pending orders with bar items that are waiting
    waiting_orders = Order.objects.filter(
        status='Pending',
        bar_status='Waiting',
        order_items__selection__item__category__title='Drink'
    ).distinct().order_by('date_ordered')[:6]  # Limit to 6 orders

    # Get preparing orders (for potential display if needed)
    preparing_orders = Order.objects.filter(
        status='Pending',
        bar_status='Preparing'
    ).prefetch_related('order_items').order_by('date_ordered')

    # Count waiting orders
    waiting_count = Order.objects.filter(
        status='Pending',
        bar_status='Waiting'
    ).count()

    context = {
        'waiting_orders': waiting_orders,
        'preparing_orders': preparing_orders,
        'waiting_count': waiting_count,
    }

    return render(request, 'bar/dashboard.html', context)


def bar_history_view(request):
    # Get completed orders (both served and completed)
    completed_orders = Order.objects.exclude(
        status='Pending',
        bar_status='Waiting'
    ).order_by('-date_ordered')

    context = {
        'completed_orders': completed_orders,
    }
    return render(request, 'bar/history.html', context)


def bar_order_ready(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.bar_status = 'Ready'
        order.save()
    return redirect('bar:bar_view')


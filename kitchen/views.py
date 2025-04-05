from django.shortcuts import render, get_object_or_404, redirect
from order.models import Order
from django.db.models import Q, Count

def kitchen_view(request):
    # Retrieve all orders with a status of 'Pending' and a kitchen status of 'Waiting'
    # Prefetch related order_items for performance and order them by date_ordered
    # Limit the results to 6 orders for display purposes
    waiting_orders = Order.objects.filter(
        status='Pending',
        kitchen_status='Waiting'
    ).prefetch_related('order_items').order_by('date_ordered')[:6]

    # Retrieve orders with a status of 'Pending' and a kitchen status of 'Preparing'
    # Prefetch related order_items for efficiency and order by date_ordered
    preparing_orders = Order.objects.filter(
        status='Pending',
        kitchen_status='Preparing'
    ).prefetch_related('order_items').order_by('date_ordered')

    # Create a queryset for waiting orders and annotate each order with a count of non-drink order items.
    # The annotation 'non_drink_count' counts all order_items where the item's category title is not "Drink"
    # (using case-insensitive matching via __iexact). Then, filter the queryset to only include orders
    # that have at least one non-drink order item.
    waiting_orders_qs = Order.objects.filter(
        status='Pending',
        kitchen_status='Waiting'
    ).annotate(
        non_drink_count=Count('order_items', filter=~Q(order_items__selection__item__category__title__iexact='Drink'))
    ).filter(non_drink_count__gt=0)

    # Count the number of distinct orders from the annotated queryset that have at least one non-drink item.
    waiting_count = waiting_orders_qs.distinct().count()

    # Build the context dictionary to pass data to the template
    context = {
        'waiting_orders': waiting_orders,
        'preparing_orders': preparing_orders,
        'waiting_count': waiting_count,
    }

    return render(request, 'kitchen/dashboard.html', context)


def history_view(request):
    # Retrieve orders that are not pending and waiting,
    # meaning they are completed (or in any state other than pending waiting)
    # Order the results in descending order based on the date_ordered
    completed_orders = Order.objects.exclude(
        status='Pending',
        kitchen_status='Waiting'
    ).order_by('-date_ordered')

    # Build the context dictionary with completed orders
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
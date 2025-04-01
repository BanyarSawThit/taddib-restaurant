from django.shortcuts import render, get_object_or_404
from order.models import Table
from order.models import Order


def table_availability(request):
    # Fetch all tables with their availability status.
    tables = Table.objects.all()
    return render(request, 'counter/table_availability.html', {'tables': tables})


def order_status(request):
    # Fetch all orders and pass them to the template
    orders = Order.objects.all()
    return render(request, 'counter/order_status.html', {'orders': orders})


# View for displaying order items
def order_items_view(request, order_id):
    order_item = get_object_or_404(Order, pk=order_id)
    return render(request, 'counter/order_items.html', {'order': order_item})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from order.models import Order, OrderItem, Table  # adjust the import as needed


def order_management(request):
    all_orders = Order.objects.all().order_by('-date_ordered')
    pending_orders = Order.objects.filter(status='Pending').order_by('-date_ordered')
    completed_orders = Order.objects.filter(status='Completed').order_by('-date_ordered')
    selected_order = all_orders.first() if all_orders.exists() else None
    context = {
        'all_orders': all_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'selected_order': selected_order,
    }
    return render(request, 'counter/order_management.html', context)


def order_detail(request, order_id):
    """
    Returns JSON details of a specific order's items.
    This view is intended to be called via AJAX.
    """
    order = get_object_or_404(Order, id=order_id)
    items = [
        {
            'id': item.id,
            'name': item.selection.item.name,
            'quantity': item.quantity,
            'price': str(item.total_price),
        }
        for item in order.order_items.all()
    ]
    data = {
        'order_id': order.id,
        'table_number': order.table.table_number,
        'items': items,
        'status': order.status,
    }
    return JsonResponse(data)


def update_order_status(request, order_id):
    """
    Receives an AJAX POST request to update an order's status.
    Expects a POST parameter 'status' (either "Pending" or "Completed").
    """
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'Completed']:
            order.status = new_status
            order.save()
            return JsonResponse({'success': True, 'new_status': order.status})
    return JsonResponse({'success': False})


def table_availability(request):
    """
    Renders a page displaying all tables with their availability.
    The status will be editable.
    """
    tables = Table.objects.all().order_by('table_number')
    context = {'tables': tables}
    return render(request, 'counter/table_availability.html', context)


def update_table_status(request, table_id):
    """
    Receives an AJAX POST request to update a table's availability status.
    """
    if request.method == 'POST':
        table = get_object_or_404(Table, id=table_id)
        new_status = request.POST.get('availability')
        if new_status is not None:
            table.availability = new_status.lower() == 'true'
            table.save()
            return JsonResponse({'success': True, 'new_status': table.availability})
    return JsonResponse({'success': False})

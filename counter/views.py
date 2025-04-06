from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from decimal import Decimal
from order.models import Order, OrderItem, Table  # adjust the import as needed


def order_management(request):
    pending_orders = Order.objects.filter(status='Pending').order_by('-date_ordered')

    # Get completed orders and add a timestamp for grouping
    completed_orders = Order.objects.filter(status='Completed').order_by('-date_ordered')

    # We'll use the date_ordered field to help separate completion batches
    # This will create separate groups even for the same table number

    # Initialize the rest of the function as before
    selected_order = None
    selected_table = None
    order_status = None
    table_orders = []

    if request.GET.get('order_id'):
        selected_order = get_object_or_404(Order, id=request.GET['order_id'])
        selected_table = selected_order.table
        order_status = selected_order.status
        table_orders = Order.objects.filter(
            table=selected_table,
            status=order_status
        ).order_by('-date_ordered')

    # Calculate totals as before
    total_amount = gst_amount = total_with_gst = Decimal('0.00')
    if selected_table and table_orders:
        for order in table_orders:
            total_amount += sum(item.total_price for item in order.order_items.all())
        gst_amount = total_amount * Decimal('0.10')
        total_with_gst = total_amount + gst_amount

    context = {
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'selected_order': selected_order,
        'selected_table': selected_table,
        'order_status': order_status,
        'table_orders': table_orders,
        'total_amount': total_amount,
        'gst_amount': gst_amount,
        'total_with_gst': total_with_gst,
    }

    return render(request, 'counter/order_management.html', context)


def order_detail(request, order_id):
    """
    Returns JSON details of a specific order's items,
    including all items from the same table with the same status.
    """
    order = get_object_or_404(Order, id=order_id)
    table = order.table
    status = order.status

    # Get all orders from the same table with the same status
    table_orders = Order.objects.filter(table=table, status=status)

    # Collect all items from all orders for this table with the same status
    items = []
    for table_order in table_orders:
        for item in table_order.order_items.all():
            items.append({
                'id': item.id,
                'name': item.selection.item.name,
                'quantity': item.quantity,
                'price': str(item.total_price),
                'order_id': table_order.id,  # Added to track which order each item belongs to
            })

    # Calculate total amounts
    total_amount = sum(Decimal(item['price']) for item in items)
    gst_amount = total_amount * Decimal('0.10')
    total_with_gst = total_amount + gst_amount

    data = {
        'order_id': order.id,
        'table_number': table.table_number,
        'status': status,
        'items': items,
        'total_amount': str(total_amount),
        'gst_amount': str(gst_amount),
        'total_with_gst': str(total_with_gst),
        'table_orders': [o.id for o in table_orders],
    }
    return JsonResponse(data)


def update_order_status(request, order_id):
    """
    Receives an AJAX POST request to update an order's status.
    When marking as completed, all pending orders from the same table are marked as completed.
    """
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')

        if new_status == 'Completed':
            # Mark all pending orders from this table as completed
            table_orders = Order.objects.filter(table=order.table, status='Pending')
            order_ids = []

            for table_order in table_orders:
                table_order.status = 'Completed'
                table_order.save()
                order_ids.append(table_order.id)

            return JsonResponse({
                'success': True,
                'new_status': 'Completed',
                'completed_orders': order_ids
            })

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

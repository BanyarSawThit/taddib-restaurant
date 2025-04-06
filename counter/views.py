from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from decimal import Decimal
from order.models import Order, OrderItem, Table  # adjust the import as needed


def order_management(request):
    all_orders = Order.objects.all().order_by('-date_ordered')
    pending_orders = Order.objects.filter(status='Pending').order_by('-date_ordered')
    completed_orders = Order.objects.filter(status='Completed').order_by('-date_ordered')

    # Get selected order if any, else set it to None
    selected_order = None
    selected_table = None
    table_pending_orders = []

    if request.GET.get('order_id'):
        selected_order = get_object_or_404(Order, id=request.GET['order_id'])
        selected_table = selected_order.table
        # Get all pending orders from the same table
        table_pending_orders = Order.objects.filter(table=selected_table, status='Pending').order_by('-date_ordered')

    # Initialize amounts to zero
    total_amount = gst_amount = total_with_gst = Decimal('0.00')

    # Calculate combined amounts for all pending orders from the selected table
    if selected_table and table_pending_orders:
        # Sum up totals from all pending orders for this table
        for order in table_pending_orders:
            total_amount += sum(item.total_price for item in order.order_items.all())

        gst_amount = total_amount * Decimal('0.10')  # 10% GST
        total_with_gst = total_amount + gst_amount

    context = {
        'all_orders': all_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'selected_order': selected_order,
        'selected_table': selected_table,
        'table_pending_orders': table_pending_orders,
        'total_amount': total_amount,
        'gst_amount': gst_amount,
        'total_with_gst': total_with_gst,
    }

    return render(request, 'counter/order_management.html', context)


def order_detail(request, order_id):
    """
    Returns JSON details of a specific order's items,
    including all pending items from the same table.
    """
    order = get_object_or_404(Order, id=order_id)
    table = order.table

    # Get all pending orders from the same table
    table_orders = Order.objects.filter(table=table, status='Pending')

    # Collect all items from all pending orders for this table
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
        'items': items,
        'status': order.status,
        'total_amount': str(total_amount),
        'gst_amount': str(gst_amount),
        'total_with_gst': str(total_with_gst),
        'table_pending_orders': [o.id for o in table_orders],
    }
    return JsonResponse(data)


def update_order_status(request, order_id):
    """
    Receives an AJAX POST request to update an order's status.
    When marking as completed, all pending orders from the same table are marked as completed.
    When marking as pending, all completed orders from the same table are marked as pending.
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

        elif new_status == 'Pending':
            # Mark all completed orders from this table as pending
            table_orders = Order.objects.filter(table=order.table, status='Completed')
            order_ids = []

            for table_order in table_orders:
                table_order.status = 'Pending'
                table_order.save()
                order_ids.append(table_order.id)

            return JsonResponse({
                'success': True,
                'new_status': 'Pending',
                'pending_orders': order_ids
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

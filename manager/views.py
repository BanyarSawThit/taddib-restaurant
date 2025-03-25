# manager/views.py
from django.shortcuts import render, get_object_or_404, redirect
from order.models import Table, Item, Category


def table_layout(request):
    tables = Table.objects.all()
    return render(request, 'manager/table_layout.html', {'tables': tables})

def edit_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    if request.method == 'POST':
        table.availability = request.POST.get('availability') == 'on'
        table.save()
        return redirect('table-layout')
    return render(request, 'manager/edit_table.html', {'table': table})

def add_table(request):
    if request.method == 'POST':
        # Find the highest current table number
        max_table = Table.objects.order_by('-table_number').first()
        new_number = max_table.table_number + 1 if max_table else 1

        # Create new table
        Table.objects.create(
            table_number=new_number,
            availability=True
        )
    return redirect('table-layout')

def delete_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    table.delete()
    return redirect('table-layout')

def edit_menu_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        # Update the item fields based on the form data
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.base_price = request.POST.get('base_price')
        item.category = Category.objects.get(id=request.POST.get('category'))
        item.save()
        return redirect('menu-items')  # Redirect back to the menu items page
    categories = Category.objects.all()  # Fetch all categories for the dropdown
    return render(request, 'manager/edit_menu_item.html', {
        'item': item,
        'categories': categories,
    })

def menu_items(request):
    items = Item.objects.all()
    total_items = items.count()  # Total number of items
    total_categories = Category.objects.count()  # Total number of categories
    return render(request, 'manager/menu_items.html', {
        'items': items,
        'total_items': total_items,
        'total_categories': total_categories,
    })
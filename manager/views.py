from django.shortcuts import render, get_object_or_404, redirect
from order.models import Table, Item, Category

# Helper functions
def _get_next_table_number():
    """Returns the next available table number"""
    last_table = Table.objects.order_by('-table_number').first()
    return last_table.table_number + 1 if last_table else 1

def _handle_category_creation(request):
    """Handles category creation from form data"""
    if request.POST.get('new_category'):
        category = Category(title=request.POST['new_category'])
        if 'new_category_image' in request.FILES:
            category.image = request.FILES['new_category_image']
        category.save()
        return category.id
    return request.POST.get('category')

# Table Views
def table_layout(request):
    """Display all tables in layout view with summary statistics"""
    tables = Table.objects.all()
    return render(request, 'manager/table_layout.html', {
        'tables': tables,
        'available_tables': tables.filter(availability=True).count()
    })

def edit_table(request, table_id):
    """Handle table availability updates"""
    table = get_object_or_404(Table, id=table_id)

    if request.method == 'POST':
        table.availability = request.POST.get('availability') == 'on'
        table.save()
        return redirect('table-layout')

    return render(request, 'manager/edit_table.html', {'table': table})

def add_table(request):
    """Create new table with next available number"""
    if request.method == 'POST':
        Table.objects.create(
            table_number=_get_next_table_number(),
            availability=True
        )
    return redirect('table-layout')

def delete_table(request, table_id):
    """Delete specified table"""
    if request.method == 'POST':
        get_object_or_404(Table, id=table_id).delete()
    return redirect('table-layout')

# Menu Item Views
def menu_items(request):
    """Display all menu items with counts"""
    return render(request, 'manager/menu_items.html', {
        'items': Item.objects.all(),
        'total_items': Item.objects.count(),
        'total_categories': Category.objects.count()
    })

def edit_menu_item(request, item_id):
    """Update existing menu item"""
    item = get_object_or_404(Item, id=item_id)

    if request.method == 'POST':
        item.name = request.POST['name']
        item.description = request.POST['description']
        item.base_price = request.POST['base_price']
        item.category_id = request.POST['category']
        item.save()
        return redirect('menu-items')

    return render(request, 'manager/edit_menu_item.html', {
        'item': item,
        'categories': Category.objects.all()
    })

def add_menu_item(request):
    """Create new menu item with optional new category"""
    if request.method == 'POST':
        new_item = Item.objects.create(
            name=request.POST.get('name', 'New Item'),
            description=request.POST.get('description', ''),
            base_price=request.POST.get('base_price', 0.00),
            category_id=_handle_category_creation(request)
        )

        if 'item_image' in request.FILES:
            new_item.image = request.FILES['item_image']
            new_item.save()

        return redirect('edit-menu-item', item_id=new_item.id)

    return render(request, 'manager/add_menu_item.html', {
        'categories': Category.objects.all()
    })

def delete_menu_item(request, item_id):
    """Delete specified menu item"""
    if request.method == 'POST':
        get_object_or_404(Item, id=item_id).delete()
    return redirect('menu-items')
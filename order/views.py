from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Table, Category, Item,  Customization, UserOrder, OrderItem
from .forms import CustomizationForm
from django.contrib import messages

# Render the table selection page
def table_view(request):
    tables = Table.objects.all()
    return render(request, 'order/table_selection.html', {'tables': tables})
def menu_page(request, table_id):


    # menu changes
    # Fetch all categories
    categories = Category.objects.all()
    # Fetch the selected category if available
    selected_category = request.GET.get('category', None)
    if selected_category:
        # Filter items by the selected category
        menu_items = Item.objects.filter(category_id=selected_category)
    else:
        # If no category is selected, show all items
        menu_items = Item.objects.all()
    # Pass categories and selected category to the template
    return render(request, 'order/menu_page.html', {
        'menu_items': menu_items,
        'categories': categories,
        'table_id': table_id,
        'selected_category': selected_category
    })


def customization_page(request, table_id, item_id):
    form = CustomizationForm()
    item = get_object_or_404(Item, pk=item_id)
    table = get_object_or_404(Table, pk=table_id)

    if request.method == 'POST':
        form = CustomizationForm(request.POST)
        if form.is_valid():
            customization = form.save(commit=False)
            customization.item = item
            customization.save()

            messages.success(request, "Item successfully added to cart!")

            # return render(request, 'order/customization_page.html', {'item':item, 'form': form, 'table_id': table_id})
            return render(request, 'cart/cart_summary.html')
        else:
            form = CustomizationForm()

    return render(request, 'order/customization_page.html', {'item':item, 'form': form, 'table_id': table_id})
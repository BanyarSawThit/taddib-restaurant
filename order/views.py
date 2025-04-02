from django.shortcuts import render, get_object_or_404, redirect
from .models import Table, Category, Item,  Selection, Order, OrderItem, MeatOption, SpicyLevel
from .forms import SelectionForm
from django.contrib import messages

# Render the table selection page
def table_view(request):
    tables = Table.objects.all()
    return render(request, 'order/table_page.html', {'tables': tables})
def menu_view(request, table_id):

    table = get_object_or_404(Table, pk=table_id)
    categories = Category.objects.all()
    menu_items = Item.objects.all()
    return render(request, 'order/menu_page.html', {
        'menu_items': menu_items,
        'categories': categories,
        'table': table,
        'table_id': table_id,
    })


def selection_view(request, table_id, item_id):
    """
    Renders the selection page for a given item and table
    Passes available spicy levels if the item supports spicy options
    """
    form = SelectionForm()
    item = get_object_or_404(Item, pk=item_id)
    table = get_object_or_404(Table, pk=table_id)
    spicylevels = SpicyLevel.objects.all() if item.has_spicy_options else None

    if request.method == 'POST':

        post_data = request.POST.copy()
        if post_data.get('meat_option') == "":
            post_data['meat_option'] = None

        if post_data.get('spicy_level') == "":
            post_data['spicy_level'] = None

        form = SelectionForm(post_data)


        if form.is_valid():
            selection = form.save(commit=False)
            selection.item = item
            selection.save()

            messages.success(request, "Item successfully added to cart!")

            return render(request, 'cart/cart_summary.html')
        else:
            # If the form is not valid, create a new empty form instance (or re-render with errors).
            messages.error(request, "There was an error with your selection. Please try again.")
            form = SelectionForm()

    return render(request, 'order/selection_page.html',
                  {'item':item,
                   'form': form,
                   'table_id': table_id,
                   'spicylevels': spicylevels,
                   })
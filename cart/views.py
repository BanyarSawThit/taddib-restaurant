from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from order.models import Item, Table, Customization, UserOrder, OrderItem
from decimal import Decimal


# Create your views here.

def selection_page(request, table_id, item_id):
    item = get_object_or_404(Item, pk=item_id)
    table = get_object_or_404(Table, pk=table_id)

    # Check if the item is already in the cart
    cart = request.session.get('cart', {'items': []})
    cart_item = next((i for i in cart['items'] if i['item_id'] == item.id), None)

    # Pre-fill form data if the item is in the cart
    initial_data = {
        'quantity': cart_item['quantity'] if cart_item else 1,
        'meat': cart_item['customization'].meat if cart_item and cart_item['customization_id'] else None,
        'spicy_level': cart_item['customization'].spicy_level if cart_item and cart_item['customization_id'] else None,
    }

    return render(request, 'order/selection_page.html', {
        'item': item,
        'table_id': table_id,
        'initial_data': initial_data,
    })


def cart_summary(request):
    cart = request.session.get('cart', {'items': []})

    cart_items = []
    for item in cart['items']:
        item_obj = get_object_or_404(Item, pk=item['item_id'])
        customization_obj = get_object_or_404(Customization, pk=item['customization_id']) if item[
            'customization_id'] else None

        cart_items.append({
            'item': item_obj,
            'customization': customization_obj,
            'quantity': item['quantity'],
            'total_price': item['total_price'],
        })

    return render(request, "cart/cart_summary.html", {'cart_items': cart_items})


def cart_add_or_update(request, table_id, item_id):
    item = get_object_or_404(Item, pk=item_id)
    table = get_object_or_404(Table, pk=table_id)

    # Get customization options from the POST request
    meat = request.POST.get('meat', None)
    spicy_level = request.POST.get('spicy_level', 'Mild')  # Provide a default value
    quantity = int(request.POST.get('quantity', 1))

    # Find or create the customization
    customization, created = Customization.objects.get_or_create(
        item=item,
        meat=meat,
        spicy_level=spicy_level,  # Ensure this is provided
        defaults={'extra_cost': Decimal(0)}  # Provide default values for other fields
    )

    # Convert all values to Decimal
    base_price = Decimal(str(item.base_price))
    selected_meat_price = Decimal(str(request.POST.get("selected_meat_price", 0)))
    selected_spicy_price = Decimal(str(request.POST.get("selected_spicy_price", 0)))
    extra_cost = Decimal(str(customization.extra_cost)) if customization else Decimal(0)

    # Calculate total price
    total_price = (base_price + selected_meat_price + selected_spicy_price + extra_cost) * Decimal(quantity)

    # Initialize the cart in the session if it doesn't exist
    if 'cart' not in request.session:
        request.session['cart'] = {'table_id': table_id, 'items': []}

    cart = request.session['cart']

    # Check if the item already exists in the cart
    item_exists = False
    for cart_item in cart['items']:
        if cart_item['item_id'] == item.id:
            # Update the existing item
            cart_item['customization_id'] = customization.id
            cart_item['quantity'] = quantity
            cart_item['total_price'] = float(total_price)
            item_exists = True
            break

    # If the item doesn't exist, add it to the cart
    if not item_exists:
        cart['items'].append({
            'item_id': item.id,
            'customization_id': customization.id,
            'quantity': quantity,
            'total_price': float(total_price)  # Convert Decimal to float for session storage
        })

    # Mark the session as modified to ensure it gets saved
    request.session.modified = True

    # Display a success message
    messages.success(request, 'Item updated in cart!' if item_exists else 'Item added to cart!')

    # Redirect to the menu page for the table
    return redirect('menu_page', table_id=table.id)  # Pass table.id instead of table


def cart_delete(request, item_id):
    cart = request.session.get('cart', {'items': []})
    cart['items'] = [item for item in cart['items'] if item['item_id'] != item_id]
    request.session.modified = True
    messages.success(request, 'Item removed from cart!')
    return redirect('cart_summary')


def cart_update(request, item_id):
    cart = request.session.get('cart', {'items': []})
    quantity = int(request.POST.get('quantity', 1))

    for item in cart['items']:
        if item['item_id'] == item_id:
            item['quantity'] = quantity
            item['total_price'] = float(Decimal(item['total_price']) / item['quantity'] * quantity)
            break

    request.session.modified = True
    messages.success(request, 'Item quantity updated!')
    return redirect('cart_summary')


def cart_confirm(request):
    """ Convert session cart into a database order. """
    cart = request.session.get('cart', None)

    if not cart or not cart['items']:
        messages.error(request, "Cart is empty!")
        return redirect('menu_page', table_id=cart.get('table_id', 1))

    table = get_object_or_404(Table, pk=cart['table_id'])

    # Create UserOrder
    user_order = UserOrder.objects.create(table=table, status="Pending")

    # Create OrderItems
    for item in cart['items']:
        customization = get_object_or_404(Customization, pk=item['customization_id']) if item[
            'customization_id'] else None
        OrderItem.objects.create(
            user_order=user_order,
            customization=customization,
            quantity=item['quantity'],
            total_price=item['total_price']
        )

    # Clear session cart
    del request.session['cart']
    request.session.modified = True

    messages.success(request, "Order placed successfully!")
    return redirect('menu_page', table_id=table.id)

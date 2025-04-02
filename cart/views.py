from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from order.models import Item, Table, Customization, UserOrder, OrderItem
from decimal import Decimal

# Display a summary of the cart
def cart_summary(request):
    # Get the cart from the session, defaulting to an empty items list if not present
    cart = request.session.get('cart', {'items': []})
    cart_items = []

    for item in cart['items']:
        # Safely retrieve the item object; raises 404 if not found
        item_obj = get_object_or_404(Item, pk=item['item_id'])
        # Retrieve the customization if provided
        customization_obj = (
            get_object_or_404(Customization, pk=item['customization_id'])
            if item.get('customization_id') else None
        )
        cart_items.append({
            'item': item_obj,
            'customization': customization_obj,
            'quantity': item['quantity'],
            'total_price': item['total_price'],
        })

    return render(request, "cart/cart_summary.html", {'cart_items': cart_items})

# Alias cart_view so that URLs pointing to 'cart_view' work correctly.
def cart_view(request):
    return cart_summary(request)

# Add an item to the cart
def cart_add(request, table_id, item_id):
    item = get_object_or_404(Item, pk=item_id)
    table = get_object_or_404(Table, pk=table_id)

    meat = request.POST.get('meat', None)
    spicy_level = request.POST.get('spicy_level', None)
    quantity = int(request.POST.get('quantity', 1))

    # Find or create the customization for the given options
    customization, created = Customization.objects.get_or_create(
        item=item, meat=meat, spicy_level=spicy_level
    )

    # Convert any price values to Decimal for accurate calculations
    selected_meat_price = Decimal(str(request.POST.get("selected_meat_price", 0)))
    selected_spicy_price = Decimal(str(request.POST.get("selected_spicy_price", 0)))

    # Calculate the total price based on base price and any extra costs
    total_price = (item.base_price + selected_meat_price + selected_spicy_price) * Decimal(quantity)

    # Initialize the cart in session if it does not exist
    if 'cart' not in request.session:
        request.session['cart'] = {'table_id': table_id, 'items': []}

    cart = request.session['cart']
    cart['items'].append({
        'item_id': item.id,
        'customization_id': customization.id,
        'quantity': quantity,
        'total_price': float(total_price),  # Store as float in the session
    })

    request.session.modified = True  # Mark the session as modified so it gets saved
    messages.success(request, 'Item added to cart!')
    return redirect('menu_page', table_id=table.id)

def cart_delete(request):
    # Implementation for deleting items from the cart (if needed)
    pass

def cart_update(request):
    # Implementation for updating the cart (if needed)
    pass

def cart_confirm(request):
    """Convert session cart into a database order."""
    cart = request.session.get('cart', None)

    if not cart or not cart.get('items'):
        messages.error(request, "Cart is empty!")
        # Redirect to the menu page. You may need to adjust table_id if necessary.
        return redirect('menu_page', table_id=cart.get('table_id', 1))

    table = get_object_or_404(Table, pk=cart['table_id'])

    # Create a new user order with status "Pending"
    user_order = UserOrder.objects.create(table=table, status="Pending")

    # Create OrderItems for each item in the cart
    for item in cart['items']:
        customization = (
            get_object_or_404(Customization, pk=item['customization_id'])
            if item.get('customization_id') else None
        )
        OrderItem.objects.create(
            user_order=user_order,
            customization=customization,
            quantity=item['quantity'],
            total_price=item['total_price']
        )

    # Clear the cart from the session
    del request.session['cart']
    request.session.modified = True

    messages.success(request, "Order placed successfully!")
    return redirect('menu_page', table_id=table.id)

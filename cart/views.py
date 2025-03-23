from django.shortcuts import render, redirect
from django.contrib import messages
from order.models import Item, Table, Customization, UserOrder, OrderItem
from decimal import Decimal

def cart_summary(request):
    """
    Display the items in the session-based cart. If an Item or Customization
    no longer exists in the database, we skip it or set it to None
    to avoid a DoesNotExist error.
    """
    cart = request.session.get('cart', {'items': []})

    cart_items = []
    for cart_item in cart['items']:
        # 1) Get the Item; if missing, skip or set item_obj to None.
        try:
            item_obj = Item.objects.get(pk=cart_item['item_id'])
        except Item.DoesNotExist:
            item_obj = None

        # 2) Get the Customization; if missing, set customization_obj to None.
        customization_obj = None
        if cart_item.get('customization_id'):
            try:
                customization_obj = Customization.objects.get(pk=cart_item['customization_id'])
            except Customization.DoesNotExist:
                customization_obj = None

        # 3) Append data for template display.
        cart_items.append({
            'item': item_obj,
            'customization': customization_obj,
            'quantity': cart_item['quantity'],
            'total_price': cart_item['total_price'],
        })

    return render(request, "cart/cart_summary.html", {'cart_items': cart_items})


def cart_add(request, table_id, item_id):
    """
    Add a new item to the session cart, creating or retrieving a Customization.
    """
    item = Item.objects.get(pk=item_id)
    table = Table.objects.get(pk=table_id)

    meat = request.POST.get('meat', None)
    spicy_level = request.POST.get('spicy_level') or 'Mild'
    allowed_spicy = ['Mild', 'Medium', 'High']
    if spicy_level not in allowed_spicy:
        spicy_level = 'Mild'

    quantity = int(request.POST.get('quantity', 1))

    # Create or retrieve the Customization
    customization, created = Customization.objects.get_or_create(
        item=item,
        meat=meat,
        spicy_level=spicy_level
    )

    # Calculate total price
    selected_meat_price = Decimal(str(request.POST.get("selected_meat_price", 0)))
    selected_spicy_price = Decimal(str(request.POST.get("selected_spicy_price", 0)))
    total_price = (item.base_price + selected_meat_price + selected_spicy_price) * Decimal(quantity)

    # Initialize session cart if missing
    if 'cart' not in request.session:
        request.session['cart'] = {'table_id': table_id, 'items': []}

    cart = request.session['cart']
    cart['items'].append({
        'item_id': item.id,
        'customization_id': customization.id,
        'quantity': quantity,
        'total_price': float(total_price)  # store as float for session
    })

    request.session.modified = True
    messages.success(request, 'Item added to cart!')

    return redirect('menu_page', table_id=table.id)


def cart_delete(request):
    # TODO: Implement if needed
    pass


def cart_update(request):
    # TODO: Implement if needed
    pass


def cart_confirm(request):
    """
    Convert the session cart into a database order. If a Customization no longer
    exists (or is not provided), create a default Customization so that OrderItem
    creation doesn't fail due to a NOT NULL constraint.
    """
    cart = request.session.get('cart', None)

    if not cart or not cart['items']:
        messages.error(request, "Cart is empty!")
        return redirect('menu_page', table_id=cart.get('table_id', 1))

    table = Table.objects.get(pk=cart['table_id'])

    # Create UserOrder
    user_order = UserOrder.objects.create(table=table, status="Pending")

    # Create OrderItems
    for cart_item in cart['items']:
        customization = None
        # Attempt to get the customization by ID
        if cart_item.get('customization_id'):
            try:
                customization = Customization.objects.get(pk=cart_item['customization_id'])
            except Customization.DoesNotExist:
                customization = None

        # If no customization is found, create a default one.
        if customization is None:
            item_obj = Item.objects.get(pk=cart_item['item_id'])
            # Create a default customization with defaults (e.g., no meat, Mild spicy)
            customization = Customization.objects.create(
                item=item_obj,
                meat=None,
                spicy_level='Mild'
            )

        OrderItem.objects.create(
            user_order=user_order,
            customization=customization,
            quantity=cart_item['quantity'],
            total_price=cart_item['total_price']
        )

    # Clear the session cart
    del request.session['cart']
    request.session.modified = True

    messages.success(request, "Order placed successfully!")
    return redirect('menu_page', table_id=table.id)

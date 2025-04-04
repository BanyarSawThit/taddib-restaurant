from django.shortcuts import render, redirect
from django.contrib import messages
from order.models import Item, Table, Selection, Order, OrderItem, SpicyLevel, MeatOption
from decimal import Decimal


def cart_add(request, table_id, item_id):
    """
    Adds an item with its custom options to the cart stored in the session.
    Expects POST data with:
      - meat_option (can be empty)
      - spicy_level (can be empty)
      - quantity
    """
    if request.method == 'POST':
        post_data = request.POST.copy()
        # Convert empty strings to None for foreign key fields.
        meat_option = post_data.get('meat_option') or None
        spicy_level = post_data.get('spicy_level') or None
        quantity = int(post_data.get('quantity', 1))

        # Build a cart item dictionary.
        cart_item = {
            'item_id': item_id,
            'table_id': table_id,
            'meat_option': meat_option,
            'spicy_level': spicy_level,
            'quantity': quantity,
        }

        # Initialize the cart in session if it doesn't exist.
        if 'cart' not in request.session:
            request.session['cart'] = []
        cart = request.session['cart']
        cart.append(cart_item)
        request.session['cart'] = cart

        messages.success(request, "Item added to cart.")
        return redirect('cart_view')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('menu_view', table_id=table_id)
def cart_view(request):
    """
    Displays the cart summary.
    Reads cart items from the session, looks up corresponding objects,
    and calculates total price.
    """
    cart = request.session.get('cart', [])
    detailed_cart = []
    total_price = 0

    for cart_item in cart:
        try:
            item = Item.objects.get(pk=cart_item['item_id'])
        except Item.DoesNotExist:
            continue

        base_price = item.base_price
        extra_meat = 0
        extra_spicy = 0

        # If a meat option was selected, look it up.
        meat_option = None
        if cart_item['meat_option']:
            try:
                meat_option = MeatOption.objects.get(pk=cart_item['meat_option'])
                extra_meat = meat_option.extra_cost
            except MeatOption.DoesNotExist:
                pass

        # If a spicy level was selected, look it up.
        spicy_level = None
        if cart_item['spicy_level']:
            try:
                spicy_level = SpicyLevel.objects.get(pk=cart_item['spicy_level'])
                # Assume extra cost is 0 for spicy levels, or add if needed.
            except SpicyLevel.DoesNotExist:
                pass

        quantity = cart_item.get('quantity', 1)
        item_total = (base_price + extra_meat + extra_spicy) * quantity
        total_price += item_total

        detailed_cart.append({
            'item': item,
            'meat_option': meat_option,
            'spicy_level': spicy_level,
            'quantity': quantity,
            'item_total': item_total,
        })

    context = {
        'cart': detailed_cart,
        'total_price': total_price,
    }
    return render(request, 'cart/cart_summary.html', context)

def cart_confirm(request):
    """
    Converts session cart into a database order and clears the cart.
    """
    cart = request.session.get('cart', None)

    if not cart or len(cart) == 0:
        messages.error(request, "Cart is empty!")
        return redirect('menu_view', table_id=1)  # fallback table

    table_id = cart[0].get('table_id')  # assume all items are for the same table
    table = Table.objects.get(pk=table_id)

    # Create the Order
    order = Order.objects.create(table=table, status="Pending")

    for cart_item in cart:
        try:
            item = Item.objects.get(pk=cart_item['item_id'])
        except Item.DoesNotExist:
            continue  # skip this item

        meat_option = None
        if cart_item['meat_option']:
            try:
                meat_option = MeatOption.objects.get(pk=cart_item['meat_option'])
            except MeatOption.DoesNotExist:
                pass

        spicy_level = None
        if cart_item['spicy_level']:
            try:
                spicy_level = SpicyLevel.objects.get(pk=cart_item['spicy_level'])
            except SpicyLevel.DoesNotExist:
                pass

        # Create Selection (optional step, if you track combinations)
        selection = Selection.objects.create(
            item=item,
            meat_option=meat_option,
            spicy_level=spicy_level
        )

        quantity = cart_item.get('quantity', 1)
        extra_meat = meat_option.extra_cost if meat_option else Decimal('0.00')
        extra_spicy = Decimal('0.00')  # Add logic if spicy levels add cost

        total_price = (item.base_price + extra_meat + extra_spicy) * quantity

        # Create OrderItem
        OrderItem.objects.create(
            order=order,
            selection=selection,
            quantity=quantity,
            total_price=total_price
        )

    # Clear session cart
    del request.session['cart']
    request.session.modified = True

    messages.success(request, "Order placed successfully!")
    return redirect('menu_
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
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

        request.session['cart'].append(cart_item)
        request.session.modified = True

        messages.success(request, "Item added to cart.")
        return redirect('menu_view', table_id=table_id)
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
    total_price = Decimal('0.00')
    total_quantity = 0
    table_id = None

    if cart:
        table_id = cart[0]['table_id']  # Get table_id from first item

    for index, cart_item in enumerate(cart):  # Added enumerate to get index
        try:
            item = Item.objects.get(pk=cart_item['item_id'])
        except Item.DoesNotExist:
            continue

        base_price = item.base_price
        extra_meat = Decimal('0.00')
        extra_spicy = Decimal('0.00')

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
        total_quantity += quantity  # Add to total quantity count
        item_total = (base_price + extra_meat + extra_spicy) * quantity
        total_price += item_total

        detailed_cart.append({
            'id': index,  # Add the index as id for editing
            'item': item,
            'meat_option': meat_option,
            'spicy_level': spicy_level,
            'quantity': quantity,
            'item_total': item_total,
        })

    context = {
        'cart': detailed_cart,
        'total_price': total_price,
        'total_quantity': total_quantity,  # Add this line
        'table_id': table_id,
    }
    return render(request, 'cart/cart_summary.html', context)


def toggle_edit_mode(request):
    """Toggle edit mode in session"""
    request.session['edit_mode'] = not request.session.get('edit_mode', False)
    return redirect('cart_view')


def update_quantities(request):
    """Handle quantity updates from form submission"""
    if request.method == 'POST':
        cart = request.session.get('cart', [])

        # Handle quantity increases
        if 'increase' in request.POST:
            item_index = int(request.POST['increase'])
            if 0 <= item_index < len(cart):
                cart[item_index]['quantity'] += 1

        # Handle quantity decreases
        elif 'decrease' in request.POST:
            item_index = int(request.POST['decrease'])
            if 0 <= item_index < len(cart):
                if cart[item_index]['quantity'] > 1:
                    cart[item_index]['quantity'] -= 1
                else:
                    del cart[item_index]

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_view')


def cart_update(request, item_index, change):
    """
    Handles quantity updates for cart items
    """
    if request.method == 'POST':
        cart = request.session.get('cart', [])

        try:
            item_index = int(item_index)
            change = int(change)

            if 0 <= item_index < len(cart):
                new_quantity = cart[item_index]['quantity'] + change

                if new_quantity < 1:
                    # Remove item if quantity would go below 1
                    del cart[item_index]
                    item_removed = True
                else:
                    cart[item_index]['quantity'] = new_quantity
                    item_removed = False

                request.session['cart'] = cart
                request.session.modified = True

                return JsonResponse({
                    'success': True,
                    'newQuantity': new_quantity,
                    'itemRemoved': item_removed
                })

        except (ValueError, IndexError) as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    }, status=400)


def cart_remove(request, item_index):
    """
    Removes an item from the cart based on its index.
    """
    cart = request.session.get('cart', [])

    try:
        item_index = int(item_index)
        # Remove the item at the specified index
        del cart[item_index]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Item removed from cart.")
    except (IndexError, ValueError):
        messages.error(request, "Item not found in cart.")

    return redirect('cart_view')


# cart/views.py
# cart/views.py
def cart_confirm(request):
    """
    Converts session cart into a database order and clears the cart.
    Redirects to payment page.
    """
    cart = request.session.get('cart', [])

    if not cart:
        messages.error(request, "Cart is empty!")
        return redirect('menu_view', table_id=1)  # fallback table

    # Get table ID from first item (assume all items are for same table)
    table_id = cart[0]['table_id']
    table = get_object_or_404(Table, pk=table_id)

    # Create the Order
    order = Order.objects.create(table=table, status="Pending")

    for cart_item in cart:
        try:
            item = Item.objects.get(pk=cart_item['item_id'])
        except Item.DoesNotExist:
            continue  # skip invalid items

        # Get meat and spicy options if they exist
        meat_option = None
        if cart_item['meat_option']:
            meat_option = get_object_or_404(MeatOption, pk=cart_item['meat_option'])

        spicy_level = None
        if cart_item['spicy_level']:
            spicy_level = get_object_or_404(SpicyLevel, pk=cart_item['spicy_level'])

        # Create selection
        selection = Selection.objects.create(
            item=item,
            meat_option=meat_option,
            spicy_level=spicy_level
        )

        # Calculate price
        quantity = cart_item.get('quantity', 1)
        extra_meat = meat_option.extra_cost if meat_option else Decimal('0.00')
        total_price = (item.base_price + extra_meat) * quantity

        # Create order item
        OrderItem.objects.create(
            order=order,
            selection=selection,
            quantity=quantity,
            total_price=total_price
        )

    # Clear cart from session
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True

    return redirect('payment_checkout', order_id=order.id)

#

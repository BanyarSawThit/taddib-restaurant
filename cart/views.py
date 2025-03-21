from django.shortcuts import render, redirect
from django.contrib import messages
from order.models import Item, Table, Selection, Order, OrderItem
from decimal import Decimal

# Create your views here.
def cart_summary(request):
    cart = request.session.get('cart', {'items': []})

    cart_items = []
    for item in cart['items']:
        item_obj = Item.objects.get(pk=item['item_id'])
        customization_obj = Selection.objects.get(pk=item['customization_id']) if item['customization_id'] else None

        cart_items.append({
            'item': item_obj,
            'customization': customization_obj,
            'quantity': item['quantity'],
            'total_price': item['total_price'],
        })

    return render(request, "cart/cart_summary.html", {'cart_items': cart_items})

def cart_add(request, table_id, item_id):
    item = Item.objects.get(pk=item_id)
    table = Table.objects.get(pk=table_id)

    meat = request.POST.get('meat', None)
    spicy_level = request.POST.get('spicy_level', None)
    quantity = int(request.POST.get('quantity', 1))

    # find or create the customization
    customization, created = Selection.objects.get_or_create(
        item=item, meat=meat, spicy_level=spicy_level
    )

    # Convert float values to Decimal before multiplying
    selected_meat_price = Decimal(str(request.POST.get("selected_meat_price", 0)))
    selected_spicy_price = Decimal(str(request.POST.get("selected_spicy_price", 0)))
    quantity = int(request.POST.get("quantity", 1))  # Ensure quantity is an integer

    # calculate total price
    extra_cost = customization.extra_cost if customization else Decimal(0)
    # total_price = Decimal(item.base_price * extra_cost) * Decimal(quantity)
    total_price = (item.base_price + selected_meat_price + selected_spicy_price) * Decimal(quantity)

    if 'cart' not in request.session:
        request.session['cart'] = {'table_id': table_id, 'items': []}

    cart = request.session['cart']
    cart['items'].append({
        'item_id': item.id,
        'customization_id': customization.id,
        'quantity': quantity,
        'total_price': float(total_price)  # Convert Decimal to float for session storage
    })

    request.session.modified = True # save session changes
    messages.success(request, 'Item added to cart!')

    return redirect('menu_page', table_id=table.id)

def cart_delete(request):
    pass
def cart_update(request):
    pass

def cart_confirm(request):
    """ Convert session cart into a database order. """
    cart = request.session.get('cart', None)

    if not cart or not cart['items']:
        messages.error(request, "Cart is empty!")
        return redirect('menu_page', table_id=cart.get('table_id', 1))

    table = Table.objects.get(pk=cart['table_id'])

    # Create Order
    user_order = Order.objects.create(table=table, status="Pending")

    # Create OrderItems
    for item in cart['items']:
        customization = Selection.objects.get(pk=item['customization_id']) if item['customization_id'] else None
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

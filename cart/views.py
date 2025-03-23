from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from order.models import Item, Customization
from .cart import Cart

@require_POST
def cart_add(request, table_id, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)

    spicy_level = request.POST.get('spicy_level', '')
    notes = request.POST.get('notes', '')

    # Use filter().first() to avoid MultipleObjectsReturned error
    customization = Customization.objects.filter(
        item=item, spicy_level=spicy_level, notes=notes
    ).first()

    if customization is None:
        customization = Customization.objects.create(
            item=item, spicy_level=spicy_level, notes=notes
        )

    cart.add(item=item, customization=customization)

    return redirect('order:table_menu', table_id=table_id)

@require_POST
def cart_update(request):
    cart = Cart(request)
    item_id = request.POST.get('item_id')
    quantity = request.POST.get('quantity')

    item = get_object_or_404(Item, id=item_id)

    try:
        quantity = int(quantity)
        if quantity > 0:
            cart.update(item=item, quantity=quantity)
        else:
            cart.remove(item)
    except (ValueError, TypeError):
        pass

    return redirect('cart:cart_summary')

def cart_delete(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)
    cart.remove(item)
    return redirect('cart:cart_summary')

def cart_summary(request):
    cart = Cart(request)
    return render(request, 'cart/summary.html', {'cart': cart})

def cart_confirm(request):
    cart = Cart(request)
    cart.clear()
    return redirect('order:index')

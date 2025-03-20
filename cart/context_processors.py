from .cart import Cart

def cart(request):
    # return the default data from our Cart
    return {'cart' : Cart(request)}

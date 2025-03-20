class Cart():
    def __init__(self, request):
        self.session = request.session

        # get the current session key if it exists
        cart = self.session.get('session_cart')

        # if the user is new, no session key! create one
        if 'session_cart' not in self.session:
            cart = self.session['session_cart'] = {}

        # make sure cart is available on all pages of site
        self.cart = cart
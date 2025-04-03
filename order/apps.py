from django.apps import AppConfig


# class OrderConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'order'
#


class OrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'order'

    def ready(self):
        # Import signals and payment-related initialization
        import order.signals  # If you'll be adding signals
        self.initialize_payment_system()

    def initialize_payment_system(self):
        """Initialize payment-related components when app starts"""
        from django.conf import settings
        import stripe

        # Configure Stripe only if keys exist
        if hasattr(settings, 'STRIPE_SECRET_KEY'):
            stripe.api_key = settings.STRIPE_SECRET_KEY
            # You could add webhook initialization here if needed
        else:
            import warnings
            warnings.warn(
                "STRIPE_SECRET_KEY not found in settings. Payments will not work.",
                RuntimeWarning
            )

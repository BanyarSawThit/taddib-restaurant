from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.table_view, name='table_view'),

    # Menu view for a specific table.
    path('table/<int:table_id>/', views.menu_view, name='menu_view'),

    # Selection view for an item on a specific table.
    # The view will allow the user to customize the item (choose meat or spicy level if available).
    path("table/<int:table_id>/item/<int:item_id>", views.selection_view, name="selection_view"),

    # payment URLs
    path('order/<int:order_id>/payment/', views.payment_checkout, name='payment_checkout'),
    path('order/<int:order_id>/payment/process/', views.process_payment, name='process_payment'),
    path('order/<int:order_id>/payment/confirmation/', views.payment_confirmation, name='payment_confirmation'),
    path('order/<int:order_id>/payment/error/', views.payment_error, name='payment_error'),
    path('order/<int:order_id>/payment/cash-receipt/', views.cash_receipt, name='cash_receipt'),
]

# Serve media files during development.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

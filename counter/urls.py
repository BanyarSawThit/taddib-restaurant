from django.urls import path
from . import views

app_name = 'counter'

urlpatterns = [
    # Orders management interface
    path('orders/', views.order_management, name='order_management'),
    # Endpoint for AJAX call to fetch order details by order id.
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    # Endpoint to update order status
    path('orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    # Table availability interface.
    path('tables/', views.table_availability, name='table_availability'),
    # Endpoint for AJAX call to update table status.
    path('tables/<int:table_id>/update/', views.update_table_status, name='update_table_status'),
]

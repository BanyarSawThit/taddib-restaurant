from django.urls import path
from . import views

urlpatterns = [
    path('tables/', views.table_availability, name='table_availability'),
    path('orders/', views.order_status, name='order_status'),
]

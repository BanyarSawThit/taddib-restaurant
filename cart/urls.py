from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.cart_summary, name='cart_summary'),
    path('add_or_update/<int:table_id>/<int:item_id>/', views.cart_add_or_update, name='cart_add_or_update'),
    path('delete/<int:item_id>/', views.cart_delete, name='cart_delete'),  # Use named argument
    path('confirm/', views.cart_confirm, name='cart_confirm'),
]
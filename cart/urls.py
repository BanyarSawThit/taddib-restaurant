from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/<int:table_id>/<int:item_id>/', views.cart_add, name='cart_add'),
    path('delete/<int:table_id>/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('confirm/', views.cart_confirm, name='cart_confirm'),
]
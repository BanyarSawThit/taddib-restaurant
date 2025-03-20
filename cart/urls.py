from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.cart_summary, name='cart_summary'),
    path('add/<int:table_id>/<int:item_id>/', views.cart_add, name='cart_add'),
    path('delete/', views.cart_delete, name='cart_delete'),
    path('update/', views.cart_update, name='cart_update'),
    path('confirm/', views.cart_confirm, name='cart_confirm'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/<int:table_id>/<int:item_id>/', views.cart_add, name='cart_add'),
    # path('delete/', views.cart_delete, name='cart_delete'),
    # path('update/', views.cart_update, name='cart_update'),
    path('confirm/', views.cart_confirm, name='cart_confirm'),
]
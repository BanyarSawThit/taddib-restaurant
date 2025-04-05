from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/<int:table_id>/<int:item_id>/', views.cart_add, name='cart_add'),
    # path('delete/', views.cart_delete, name='cart_delete'),
    # path('update/', views.cart_update, name='cart_update'),
    path('confirm/', views.cart_confirm, name='cart_confirm'),
    path('remove/<int:item_index>/', views.cart_remove, name='cart_remove'),
    path('update/<int:item_index>/<int:change>/', views.update_quantities, name='update_quantity'),
    path('toggle-edit/', views.toggle_edit_mode, name='toggle_edit_mode'),
    path('update/<int:item_index>/<int:change>/', views.cart_update, name='cart_update'),
]
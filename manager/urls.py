from django.urls import path
from . import views

urlpatterns = [
    path('tables/', views.table_layout, name='table-layout'),
    path('tables/edit/<int:table_id>/', views.edit_table, name='edit-table'),
    path('tables/add/', views.add_table, name='add-table'),
    path('tables/delete/<int:table_id>/', views.delete_table, name='delete-table'),
    path('menu/', views.menu_items, name='menu-items'),
    path('menu/edit/<int:item_id>/', views.edit_menu_item, name='edit-menu-item'),
]
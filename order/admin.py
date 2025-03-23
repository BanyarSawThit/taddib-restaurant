from django.contrib import admin
from .models import Table, Category, Item, Customization, UserOrder, OrderItem

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'capacity']
    search_fields = ['number']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(Customization)
class CustomizationAdmin(admin.ModelAdmin):
    list_display = ['item', 'spicy_level', 'meat']
    list_filter = ['spicy_level', 'meat', 'item']
    search_fields = ['item__name', 'spicy_level', 'meat']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(UserOrder)
class UserOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'order_time', 'total_price']
    list_filter = ['order_time', 'table']
    search_fields = ['id', 'table__number']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'item', 'customization', 'quantity']
    list_filter = ['item']
    search_fields = ['order__id', 'item__name']

from django.contrib import admin
from .models import Table, Category, Customization, UserOrder, OrderItem, Item

admin.site.register((Table,Category, Customization, UserOrder, OrderItem, Item))

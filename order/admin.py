from django.contrib import admin
from .models import Table, Category, Selection, Order, OrderItem, Item, MeatOption, SpicyLevel

admin.site.register((Table,Category, Selection, Order, OrderItem, Item, MeatOption, SpicyLevel))

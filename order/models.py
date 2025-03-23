from django.db import models

class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"Table {self.number} (Seats: {self.capacity})"

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='items/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Customization(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    spicy_level = models.CharField(max_length=50, null=True, blank=True)
    meat = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        unique_together = ('item', 'spicy_level', 'meat')

    def __str__(self):
        spicy = self.spicy_level or 'No Spice'
        meat_choice = self.meat or 'No Meat'
        return f"{self.item.name} - {spicy} - {meat_choice}"

class UserOrder(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Order {self.id} at Table {self.table.number}"

class OrderItem(models.Model):
    order = models.ForeignKey(UserOrder, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    customization = models.ForeignKey(Customization, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

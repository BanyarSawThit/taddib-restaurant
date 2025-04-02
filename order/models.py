import qrcode
from django.db import models
from django.core.files.base import ContentFile
from io import BytesIO

# ------------------------------------------------------------------------------
# Table Model
# ------------------------------------------------------------------------------
class Table(models.Model):
    table_number = models.PositiveIntegerField(unique=True)
    availability = models.BooleanField(default=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def generate_qr_code(self):
        """
        Generates a QR code that directs to the table's menu page.
        """
        qr = qrcode.make(f"http://localhost:8000/order/{self.table_number}/menu/")
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f'table_{self.table_number}.png', ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Table {self.table_number}"


# ------------------------------------------------------------------------------
# Category Model
# ------------------------------------------------------------------------------
class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title

# ------------------------------------------------------------------------------
# Menu Item Model
# ------------------------------------------------------------------------------
class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    item_image = models.ImageField(default='supernova.jpg', blank=True)
    base_price = models.DecimalField(max_digits=5, decimal_places=2)
    has_meat_options = models.BooleanField(default=True)
    has_spicy_options = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} , {self.category.title}"

class Customization(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='customizations')
    meat = models.CharField(max_length=50, choices=[('Beef', 'Beef'), ('Chicken', 'Chicken')], blank=True, null=True)
    spicy_level = models.CharField(max_length=50, choices=[('Mild', 'Mild'), ('Medium', 'Medium'), ('High', 'High')])
    extra_cost = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.item.name} ( meat-{self.meat} , spicy-{self.spicy_level})'

class UserOrder(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')])

    def __str__(self):
        return f'Order {self.id} , Table {self.table.table_number} ({self.status})'

class OrderItem(models.Model):
    user_order = models.ForeignKey(UserOrder, on_delete=models.CASCADE)
    customization= models.ForeignKey(Customization, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customization.item.name} x {self.quantity} - Order {self.user_order.id}"


class Selection:
    pass


class Order:
    pass


class MeatOption:
    pass


class SpicyLevel:
    pass
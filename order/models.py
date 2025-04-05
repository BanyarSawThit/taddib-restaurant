from decimal import Decimal
import qrcode
from django.db import models
from django.core.files.base import ContentFile
from io import BytesIO
from django.conf import settings
from django.urls import reverse


# ------------------------------------------------------------------------------
# Table Model: Represents a dining table in the restaurant.
# ------------------------------------------------------------------------------
class Table(models.Model):
    # A unique number identifying each table.
    table_number = models.PositiveIntegerField(unique=True)
    # Indicates if the table is currently available (True by default).
    availability = models.BooleanField(default=True)
    # Stores the QR code image for the table; optional field.
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True,
                                help_text='create a qr code everytime a table is saved!')

    def generate_qr_code(self):
        """
        Generates a QR code that directs to the table's menu page.
        """
        # Create a QR code with a URL that includes the table number.
        qr = qrcode.make(f"http://localhost:8000/order/{self.table_number}/menu/")
        buffer = BytesIO()  # Buffer to temporarily hold the image data.
        qr.save(buffer, format="PNG")  # Save the QR code image into the buffer.
        # Save the image to the qr_code field without immediately saving the model.
        self.qr_code.save(f'table_{self.table_number}.png', ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        """
        Overrides the default save method.
        Generates a QR code if one does not already exist before saving the instance.
        """
        if not self.qr_code:
            self.generate_qr_code()
        # Call the parent save method to perform the actual database save.
        super().save(*args, **kwargs)

    def _str_(self):
        """
        String representation of the Table.
        """
        return f"Table {self.table_number}"


# ------------------------------------------------------------------------------
# Category Model: Represents a category for menu items (e.g., Appetizers, Drinks).
# ------------------------------------------------------------------------------
class Category(models.Model):
    # Title of the category.
    title = models.CharField(max_length=100)
    # Optional image representing the category.
    image = models.ImageField(blank=True, null=True)

    class Meta:
        # Specifies plural name to be displayed in the admin interface.
        verbose_name_plural = "Categories"

    def _str_(self):
        """
        String representation of the Category.
        """
        return self.title


# ------------------------------------------------------------------------------
# Item Model: Represents a menu item.
# ------------------------------------------------------------------------------
class Item(models.Model):
    # Name of the menu item.
    name = models.CharField(max_length=100)
    # Detailed description of the menu item; optional.
    description = models.TextField(null=True, blank=True)
    # Relationship to a category; if a category is deleted, all related items are deleted.
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    # Optional image of the menu item.
    image = models.ImageField(blank=True, null=True)
    # Base price of the menu item.
    base_price = models.DecimalField(max_digits=6, decimal_places=2)
    # Indicates whether this item has additional meat options.
    has_meat_options = models.BooleanField(default=False)
    # Indicates whether this item has spicy options.
    has_spicy_options = models.BooleanField(default=False)

    def get_meat_options(self):
        """
        Returns available meat options if this item supports them;
        otherwise, returns an empty queryset.
        """
        if self.has_meat_options:
            # Could later be extended to filter options specific to this item.
            return MeatOption.objects.all()
        return MeatOption.objects.none()

    def _str_(self):
        """
        String representation of the Item.
        """
        return f"{self.name} , {self.category.title}"


# ------------------------------------------------------------------------------
# MeatOption Model: Represents extra meat options that may add an extra cost.
# ------------------------------------------------------------------------------
class MeatOption(models.Model):
    # Name of the meat option; must be unique.
    name = models.CharField(max_length=50, unique=True)
    # Extra cost associated with the meat option.
    extra_cost = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def _str_(self):
        """
        String representation of the MeatOption.
        """
        return f"{self.name} (+S${self.extra_cost})"


# ------------------------------------------------------------------------------
# SpicyLevel Model: Represents different levels of spiciness.
# ------------------------------------------------------------------------------
class SpicyLevel(models.Model):
    # Name of the spicy level; must be unique.
    name = models.CharField(max_length=50, unique=True,
                            help_text="Label for the spiciness level (e.g., Mild, Medium, Hot)")

    def _str_(self):
        """
        String representation of the SpicyLevel.
        """
        return self.name


# ------------------------------------------------------------------------------
# Selection Model: Represents the customization choices for an item.
# ------------------------------------------------------------------------------
class Selection(models.Model):
    # Relationship to a menu item.
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='selections')
    # Optional meat option; if deleted, this field is set to null.
    meat_option = models.ForeignKey(MeatOption, on_delete=models.SET_NULL, null=True, blank=True)
    # Optional spicy level; if deleted, this field is set to null.
    spicy_level = models.ForeignKey(SpicyLevel, on_delete=models.SET_NULL, null=True, blank=True)

    def get_extra_cost(self):
        """
        Returns additional cost from the selected meat option if available.
        """
        return Decimal(self.meat_option.extra_cost) if self.meat_option else Decimal(0.00)

    def _str_(self):
        """
        String representation of the Selection.
        Combines the item name with the selected meat and spicy options.
        """
        meat_str = f"Meat: {self.meat_option}" if self.meat_option else "No Meat"
        spicy_str = f"Spicy: {self.spicy_level}" if self.spicy_level else "No Spicy"
        return f"{self.item.name} ({meat_str}, {spicy_str})"


# ------------------------------------------------------------------------------
# Order Model: Represents a customer's order.
# ------------------------------------------------------------------------------
class Order(models.Model):
    # Link to the table where the order was placed.
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    # Automatically set the date and time when the order is created.
    date_ordered = models.DateTimeField(auto_now_add=True)

    # Possible statuses for an order.
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        # Additional statuses (e.g., 'In Progress', 'Cancelled') can be added later.
    ]
    # Current status of the order, defaults to 'Pending'.
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    def get_total(self):
        """
        Calculates the total amount for the order by summing the total prices of all associated order items.
        """
        return sum(item.total_price for item in self.order_items.all())

    kitchen_status_choices = [
        ('Waiting', 'Waiting'),
        ('Preparing', 'Preparing'),
        ('Ready', 'Ready'),
    ]
    kitchen_status = models.CharField(max_length=50, choices=kitchen_status_choices, default='Waiting')

    bar_status = models.CharField(max_length=50, choices=kitchen_status_choices, default='Waiting')

    def get_kitchen_items(self):
        return self.order_items.exclude(selection_itemcategory_title='Drink')

    def get_bar_items(self):
        return self.order_items.filter(selection_itemcategory_title='Drink')

    def _str_(self):
        """
        String representation of the Order.
        Includes the order ID, table number, and current status.
        """
        return f'Order {self.id} , Table {self.table.table_number} ({self.status}), kitchen ({self.kitchen_status}), bar ({self.bar_status})'


# ------------------------------------------------------------------------------
# OrderItem Model: Represents an individual item within an order.
# ------------------------------------------------------------------------------
class OrderItem(models.Model):
    # Link to the parent order; this field is non-nullable.
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    # Link to the selected customization for the item.
    selection = models.ForeignKey(Selection, on_delete=models.CASCADE)
    # Quantity of the selected item; defaults to 1.
    quantity = models.PositiveIntegerField(default=1)
    # Total price calculated from the base price, any extra costs, and the quantity.
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        """
        Overrides the save method to calculate and update the total price before saving.
        It multiplies the sum of the base price and any extra cost by the quantity.
        """
        self.total_price = (self.selection.item.base_price + self.selection.get_extra_cost()) * self.quantity
        super().save(*args, **kwargs)

    def _str_(self):
        """
        String representation of the OrderItem.
        Displays the item's name, quantity, and the associated order's ID.
        """
        return f"{self.selection.item.name} x {self.quantity} (Order {self.order.pk})"


# models.py
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('cash', 'Cash'),
        ('paynow', 'PayNow'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    qr_code = models.ImageField(upload_to='paynow_qr/', blank=True, null=True)
    billing_email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def _str_(self):
        return f"Payment #{self.id} for Order #{self.order.id} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Auto-set amount if not provided"""
        if not self.amount and self.order:
            self.amount = self.order.get_total()
        super().save(*args, **kwargs)

    def generate_paynow_qr(self):
        """Generate QR code for PayNow payments"""
        if self.payment_method == 'paynow' and not self.qr_code:
            qr_img = qrcode.make(f"PAYNOW|{self.order.id}|{self.amount}")
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            self.qr_code.save(f'paynow_{self.order.id}.png', ContentFile(buffer.getvalue()))
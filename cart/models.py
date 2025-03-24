from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)  # Ensure this field exists
    # Add other fields if necessary

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Ensure this field exists
    # Add other fields if necessary

    def __str__(self):
        return self.name


class Customization(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='customizations')
    meat = models.CharField(max_length=50, choices=[('Beef', 'Beef'), ('Chicken', 'Chicken')], blank=True, null=True)
    spicy_level = models.CharField(max_length=50, choices=[('Mild', 'Mild'), ('Medium', 'Medium'), ('High', 'High')], blank=True, null=True)  # Make optional
    extra_cost = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.item.name} (meat={self.meat}, spicy={self.spicy_level})'
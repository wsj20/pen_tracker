from django.db import models
from django.db.models.functions import Length

# Create your models here.
class PenModel(models.Model):
    brand = models.CharField(max_length=32)
    name = models.CharField(max_length=32)

    #Organising list by brand, length of name then by name itelf
    class Meta:
        ordering = ['brand', Length('name'), 'name']

    def __str__(self):
        return f"{self.brand} {self.name}"
    
class Supplier(models.Model):
    name = models.CharField(max_length=64)
    website = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.name}"
    
class Pen(models.Model):

    STATUS_IN_STOCK = 'IN_STOCK'
    STATUS_UNDER_REFURB = 'UNDER_REFURB'
    STATUS_LISTED = 'LISTED'
    STATUS_SOLD = 'SOLD'

    STATUS_CHOICES = [
        (STATUS_IN_STOCK, 'In Stock'),
        (STATUS_UNDER_REFURB, 'Under Refurbishment'),
        (STATUS_LISTED, 'Listed'),
        (STATUS_SOLD, 'Sold'),
    ]

    pen_model = models.ForeignKey(PenModel, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)    
    colour = models.CharField(max_length=32)
    description = models.CharField(max_length=100)
    acquisition_cost = models.DecimalField(max_digits=8, decimal_places=2)
    acquisition_date = models.DateField()
    ebay_item_id = models.CharField(max_length=20, blank=True, null=True)
    refurb_note = models.TextField(blank=True)

    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default=STATUS_IN_STOCK
    )

    def __str__(self):
        return f"{self.pen_model} - {self.colour} -- {self.description}"


class Part(models.Model):
    name = models.CharField(max_length=64)
    quantity_on_hand = models.IntegerField()
    pen_model = models.ForeignKey(PenModel, on_delete=models.SET_NULL, blank=True, null=True)
    cost_per_unit = models.DecimalField(max_digits=8, decimal_places=2, blank=True, default=0)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.pen_model} - {self.name} - {self.description}"
    
class PenPartsUsage(models.Model):
    pen = models.ForeignKey(Pen, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    quantity_used = models.IntegerField(default=1)
    cost_at_time_of_use = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity_used} x {self.part.name} used on {self.pen}"
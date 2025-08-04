from django.db import models

# Create your models here.
class PenModel(models.Model):
    brand = models.CharField(max_length=32)
    name = models.CharField(max_length=32)

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



    
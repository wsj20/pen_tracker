from django.db import models
from inventory.models import Pen

# Create your models here.
class Expense(models.Model):

    CATEGORY_SHIPPING = 'SHIPPING'
    CATEGORY_TOOLS = 'TOOLS'
    CATEGORY_FEES = 'FEES'
    CATEGORY_OTHER = 'OTHER'

    CATEGORY_CHOICES = [
        (CATEGORY_SHIPPING, 'Shipping Supplies'),
        (CATEGORY_TOOLS, 'Tools'),
        (CATEGORY_FEES, 'eBay Fees'),
        (CATEGORY_OTHER, 'Other'),
    ]

    description = models.CharField(max_length=64)
    date_incurred = models.DateField()
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,  
        default=CATEGORY_OTHER
    )

    def __str__(self):
        return f"{self.date_incurred} - {self.description} - £{self.cost}"
    
class Sale(models.Model):
    #One to one as Pen can only be linked to ONE sale.
    pen = models.OneToOneField(Pen, on_delete=models.PROTECT)
    date_sold = models.DateField()
    final_sale_price = models.DecimalField(max_digits=8, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=8, decimal_places=2)
    transaction_fee = models.DecimalField(max_digits=8, decimal_places=2)
    other_fees = models.DecimalField(max_digits=8, decimal_places=2, default=0.25)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Sale of {self.pen} on {self.date_sold} for {self.final_sale_price}"

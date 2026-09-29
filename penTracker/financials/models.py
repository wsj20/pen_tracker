from django.db import models
from inventory.models import Pen


class Expense(models.Model):

    HMRC_STOCK = 'stock_materials'
    HMRC_POSTAGE = 'postage_stationery'
    HMRC_FEES = 'platform_fees'
    HMRC_TOOLS = 'equipment_tools'
    HMRC_OTHER = 'other_allowable'

    HMRC_CATEGORY_CHOICES = [
        (HMRC_STOCK, 'Stock, Materials & Resale Goods'),
        (HMRC_POSTAGE, 'Postage, Carriage & Stationery'),
        (HMRC_FEES, 'Bank, Credit Card & Financial Charges'),
        (HMRC_TOOLS, 'Equipment & Small Tools'),
        (HMRC_OTHER, 'Other Allowable Expenses'),
    ]

    description = models.CharField(max_length=64)
    date_incurred = models.DateField()
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    hmrc_category = models.CharField(
        max_length=32,
        choices=HMRC_CATEGORY_CHOICES,
        default=HMRC_STOCK
    )

    def __str__(self):
        return f"{self.date_incurred} - {self.description} - £{self.cost}"


class Sale(models.Model):
    pen = models.OneToOneField(Pen, on_delete=models.PROTECT)
    date_sold = models.DateField()
    final_sale_price = models.DecimalField(max_digits=8, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=8, decimal_places=2)
    transaction_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    other_fees = models.DecimalField(max_digits=8, decimal_places=2, default=0.25)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Sale of {self.pen} on {self.date_sold} for £{self.final_sale_price}"
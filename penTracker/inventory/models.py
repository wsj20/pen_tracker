from django.db import models
from django.db.models.functions import Length
from django.db.models import Sum


class PenModel(models.Model):
    brand = models.CharField(max_length=32)
    name = models.CharField(max_length=32)

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
    STATUS_AWAITING_PARTS = 'AWAITING_PARTS'
    STATUS_LISTED = 'LISTED'
    STATUS_SOLD = 'SOLD'
    STATUS_DONOR = 'DONOR'

    STATUS_CHOICES = [
        (STATUS_IN_STOCK, 'In Stock'),
        (STATUS_UNDER_REFURB, 'Under Refurbishment'),
        (STATUS_AWAITING_PARTS, 'Awaiting Parts'),
        (STATUS_LISTED, 'Listed'),
        (STATUS_SOLD, 'Sold'),
        (STATUS_DONOR, 'Donor / Parts Pen'),
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
    
    def calculate_total_cost(self):
        parts_cost_result = self.parts_used.aggregate(
            total=Sum('cost_at_time_of_use')
        )
        parts_cost = parts_cost_result['total'] or 0
        
        return self.acquisition_cost + parts_cost
    
    def calculate_net_profit(self):
        if not hasattr(self, 'sale'):
            return None
        
        pen_total_cost = self.calculate_total_cost()
        sale_costs = self.sale.transaction_fee + self.sale.other_fees + self.sale.shipping_cost
        revenue = self.sale.final_sale_price + self.sale.shipping_charge
        
        return revenue - (pen_total_cost + sale_costs)


class Part(models.Model):
    name = models.CharField(max_length=64)
    quantity_on_hand = models.IntegerField()
    cost_per_unit = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    harvested_from = models.ForeignKey(
        Pen, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='harvested_parts'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.quantity_on_hand} in stock @ £{self.cost_per_unit} ea)"


class PenPartsUsage(models.Model):
    pen = models.ForeignKey(Pen, on_delete=models.CASCADE, related_name='parts_used')
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    quantity_used = models.IntegerField(default=1)
    cost_at_time_of_use = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity_used} x {self.part.name} used on {self.pen}"
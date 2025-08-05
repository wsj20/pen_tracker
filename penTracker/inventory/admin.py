from django.contrib import admin
from .models import PenModel, Supplier, Pen, Part, PenPartsUsage

# Register your models here.
admin.site.register(PenModel)
admin.site.register(Supplier)
admin.site.register(Pen)
admin.site.register(Part)
admin.site.register(PenPartsUsage)
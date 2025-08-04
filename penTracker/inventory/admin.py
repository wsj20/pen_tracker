from django.contrib import admin
from .models import PenModel, Supplier, Pen

# Register your models here.
admin.site.register(PenModel)
admin.site.register(Supplier)
admin.site.register(Pen)
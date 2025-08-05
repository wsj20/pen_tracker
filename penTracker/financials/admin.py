from django.contrib import admin
from .models import Expense, Sale

# Register your models here.
admin.site.register(Sale)
admin.site.register(Expense)
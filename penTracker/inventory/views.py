from django.shortcuts import render
from .models import Pen

# Create your views here.

def sales_inventory(request):
    all_pens = Pen.objects.all()

    context = {
        'pens':all_pens
    }

    return render(request, 'inventory/sales_inventory.html', context)
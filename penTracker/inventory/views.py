from django.shortcuts import render, redirect, get_object_or_404
from .models import Pen
from .forms import PenForm, PenModelForm, PenSupplierForm

# Create your views here.

#Display current inventory
def pen_list(request):
    all_pens = Pen.objects.all()
    context = {
        'pens':all_pens
    }
    return render(request, 'inventory/pen_list.html', context)

#Form to add new pen
def add_pen(request):
    if request.method == 'POST':
        form = PenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pen-list')
    else:
        form = PenForm()

    context = {'form': form}
    return render(request, 'inventory/pen_form.html', context)

#Add new pen model:
def add_pen_model(request):
    if request.method == 'POST':
        form = PenModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pen-add')
    else:
        form = PenModelForm()

    context = {'form': form}
    return render(request, 'inventory/pen_model_form.html', context)

def add_pen_supplier(request):
    if request.method == "POST":
        form = PenSupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pen-add')
    else:
        form = PenSupplierForm()
    context = {'form':form}
    return render(request, 'inventory/pen_supplier_form.html', context)
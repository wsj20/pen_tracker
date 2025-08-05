from django.shortcuts import render, redirect, get_object_or_404
from .models import Pen
from .forms import PenForm, PenModelForm, PenSupplierForm, Part, PartForm

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

#Delete Specified Pen
def delete_pen(request, pk):
    pen_to_delete = get_object_or_404(Pen, pk=pk)

    if request.method == "POST":
        pen_to_delete.delete()
        return redirect('pen-list')
    return redirect('pen-list')

# MAINLY FOR JS LATER BUT ADDED NOW
def edit_pen(request, pk):
    pen_to_edit = get_object_or_404(Pen, pk=pk)

    if request.method == 'POST':
        # When the user saves, populate the form with the submitted data
        # AND specify the instance to update the correct pen record.
        form = PenForm(request.POST, instance=pen_to_edit)
        if form.is_valid():
            form.save()
            return redirect('pen-list')
    else:
        # For the initial GET request, populate the form with the existing pen's data
        form = PenForm(instance=pen_to_edit)
    
    context = {
        'form': form,
    }
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

def pen_detail(request, pk):
    pen = get_object_or_404(Pen, pk=pk)

    context = {
        'pen': pen
    }
    return render(request, 'inventory/pen_detail.html', context)

def part_list(request):
    all_parts = Part.objects.order_by('description')
    context = {
        'parts': all_parts
    }
    return render(request, 'inventory/part_list.html', context)

def add_part(request):
    if request.method == "POST":
        form = PartForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('part-list')
    else:
        form = PartForm()
    context = {
        'form':form
    }
    return render(request, 'inventory/part_form.html', context)

def edit_part(request, pk):
    part_to_edit = get_object_or_404(Part, pk=pk)

    if request.method == 'POST':
        form = PartForm(request.POST, instance=part_to_edit)
        if form.is_valid():
            form.save()
            return redirect('part-list')
    else:
        form = PartForm(instance=part_to_edit)
    context = {
        'form': form,
    }
    return render(request, 'inventory/part_form.html', context)

def delete_part(request, pk):
    pen_to_delete = get_object_or_404(Part, pk=pk)

    if request.method == "POST":
        pen_to_delete.delete()
        return redirect('part-list')
    return redirect('part-list')
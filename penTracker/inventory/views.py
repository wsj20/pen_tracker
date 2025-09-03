from django.shortcuts import render, redirect, get_object_or_404
from .models import Pen
from .forms import PenForm, PenModelForm, PenSupplierForm, Part, PartForm, PenPartUsageForm, PenPartsUsage
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField
# Create your views here.

#Display current inventory
@login_required
def pen_list(request):
    all_pens = Pen.objects.exclude(status=Pen.STATUS_SOLD).order_by('status')
    context = {
        'pens':all_pens
    }
    return render(request, 'inventory/pen_list.html', context)

#Form to add new pen
@login_required
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
@login_required
def delete_pen(request, pk):
    pen_to_delete = get_object_or_404(Pen, pk=pk)

    if request.method == "POST":
        pen_to_delete.delete()
        return redirect('pen-list')
    return redirect('pen-list')

# MAINLY FOR JS LATER BUT ADDED NOW
@login_required
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
@login_required
def add_pen_model(request):

    next_url = request.GET.get('next', 'pen-list') 

    if request.method == 'POST':
        form = PenModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(next_url) 
    else:
        form = PenModelForm()
    
    context = {
        'form': form,
        'next_url': next_url #url for cancel button
    }
    return render(request, 'inventory/pen_model_form.html', context)

@login_required
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

@login_required
def pen_detail(request, pk):
    pen = get_object_or_404(Pen, pk=pk)
    
    if request.method == 'POST':
        form = PenPartUsageForm(request.POST)
        if form.is_valid():
            # Create the object in memory but don't save to the database just yet
            usage = form.save(commit=False)
            # Assign the current pen to the 'pen' field of the usage record
            usage.pen = pen
            usage.cost_at_time_of_use = usage.part.cost_per_unit
            usage.save()

            # Update Parts Inventory
            # Get the part that was just used
            part_used = usage.part
            # Decrease its quantity_on_hand by the amount used
            part_used.quantity_on_hand -= usage.quantity_used
            part_used.save()

            return redirect('pen-detail', pk=pen.pk)
    else:
        form = PenPartUsageForm()

    parts_used = PenPartsUsage.objects.filter(pen=pen)
    
    context = {
        'pen': pen,
        'parts_used': parts_used,  #Pass the list to the template
        'form': form,              #Pass the blank form to the template
    }
    return render(request, 'inventory/pen_detail.html', context)

@login_required
def part_list(request):
    #only fetch parts with a quantity > 0
    all_parts = Part.objects.filter(quantity_on_hand__gt=0).annotate(
        is_generic=Case(
            When(pen_model__isnull=True, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by('is_generic', 'pen_model__brand', 'pen_model__name', 'name')

    context = {
        'parts': all_parts
    }
    return render(request, 'inventory/part_list.html', context)

@login_required
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

@login_required
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

@login_required
def delete_part(request, pk):
    pen_to_delete = get_object_or_404(Part, pk=pk)

    if request.method == "POST":
        pen_to_delete.delete()
        return redirect('part-list')
    return redirect('part-list')

@login_required
def delete_part_usage(request, pk):
    usage_to_delete = get_object_or_404(PenPartsUsage, pk=pk)
    # We need to know which pen's detail page to redirect back to
    pen_id = usage_to_delete.pen.pk

    if request.method == 'POST':
        # Reverse the inventory change
        # Get the part associated with this usage record
        part_to_reimburse = usage_to_delete.part
        # Add the quantity from the usage record back to the main inventory
        part_to_reimburse.quantity_on_hand += usage_to_delete.quantity_used
        part_to_reimburse.save()

        # Now that the inventory is corrected, delete the usage record itself
        usage_to_delete.delete()
        
        return redirect('pen-detail', pk=pen_id)

    return redirect('pen-detail', pk=pen_id)
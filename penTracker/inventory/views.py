from django.shortcuts import render, redirect, get_object_or_404
from .models import Pen, Part, PenPartsUsage
from .forms import PenForm, PenModelForm, PenSupplierForm, PartForm, PenPartUsageForm
from django.contrib.auth.decorators import login_required


@login_required
def pen_list(request):
    status_filter = request.GET.get('status')
    
    if status_filter == 'donor':
        pens = Pen.objects.filter(status=Pen.STATUS_DONOR)
    else:
        pens = Pen.objects.exclude(status__in=[Pen.STATUS_SOLD, Pen.STATUS_DONOR]).order_by('status')

    context = {
        'pens': pens,
        'current_tab': status_filter or 'active'
    }
    return render(request, 'inventory/pen_list.html', context)


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


@login_required
def delete_pen(request, pk):
    pen_to_delete = get_object_or_404(Pen, pk=pk)
    if request.method == "POST":
        pen_to_delete.delete()
        return redirect('pen-list')
    return redirect('pen-list')


@login_required
def edit_pen(request, pk):
    pen_to_edit = get_object_or_404(Pen, pk=pk)

    if request.method == 'POST':
        form = PenForm(request.POST, instance=pen_to_edit)
        if form.is_valid():
            form.save()
            return redirect('pen-list')
    else:
        form = PenForm(instance=pen_to_edit)
    
    context = {'form': form}
    return render(request, 'inventory/pen_form.html', context)


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
        'next_url': next_url
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
    context = {'form': form}
    return render(request, 'inventory/pen_supplier_form.html', context)


@login_required
def pen_detail(request, pk):
    pen = get_object_or_404(Pen, pk=pk)
    
    if request.method == 'POST':
        form = PenPartUsageForm(request.POST)
        if form.is_valid():
            usage = form.save(commit=False)
            usage.pen = pen
            usage.cost_at_time_of_use = usage.part.cost_per_unit
            usage.save()

            part_used = usage.part
            part_used.quantity_on_hand -= usage.quantity_used
            part_used.save()

            return redirect('pen-detail', pk=pen.pk)
    else:
        form = PenPartUsageForm()

    parts_used = PenPartsUsage.objects.filter(pen=pen)
    
    context = {
        'pen': pen,
        'parts_used': parts_used,
        'form': form,
    }
    return render(request, 'inventory/pen_detail.html', context)


@login_required
def part_list(request):
    all_parts = Part.objects.filter(quantity_on_hand__gt=0)
    context = {'parts': all_parts}
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
    context = {'form': form}
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
    context = {'form': form}
    return render(request, 'inventory/part_form.html', context)


@login_required
def delete_part(request, pk):
    part_to_delete = get_object_or_404(Part, pk=pk)

    if request.method == "POST":
        part_to_delete.delete()
        return redirect('part-list')
    return redirect('part-list')


@login_required
def delete_part_usage(request, pk):
    usage_to_delete = get_object_or_404(PenPartsUsage, pk=pk)
    pen_id = usage_to_delete.pen.pk

    if request.method == 'POST':
        part_to_reimburse = usage_to_delete.part
        part_to_reimburse.quantity_on_hand += usage_to_delete.quantity_used
        part_to_reimburse.save()

        usage_to_delete.delete()
        return redirect('pen-detail', pk=pen_id)

    return redirect('pen-detail', pk=pen_id)
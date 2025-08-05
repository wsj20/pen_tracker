from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Sale
from .forms import ExpenseForm, SaleForm
from inventory.models import Pen, PenPartsUsage
from django.db.models import Sum, F
from decimal import Decimal

# Create your views here.
def expense_list(request):
    all_expenses = Expense.objects.all()
    context = {
        'expenses':all_expenses
    }
    return render(request, 'financials/expense_list.html', context)

def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense-list')
    else:
        form = ExpenseForm()

    context = {'form': form}
    return render(request, 'financials/expense_form.html', context)

def edit_expense(request, pk):
    expense_to_edit = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense_to_edit)
        if form.is_valid():
            form.save()
            return redirect('expense-list')
    else:
        form = ExpenseForm(instance=expense_to_edit)
    
    context = {'form': form}
    return render(request, 'financials/expense_form.html', context)


def delete_expense(request, pk):
    expense_to_delete = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense_to_delete.delete()
        return redirect('expense-list')
    
    return redirect('expense-list')

def record_sale(request, pen_pk):
    pen_to_sell = get_object_or_404(Pen, pk=pen_pk)

    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.pen = pen_to_sell
            sale.save()

            pen_to_sell.status = Pen.STATUS_SOLD
            pen_to_sell.save()

            return redirect('pen-detail', pk=pen_to_sell.pk)
        
    else:
        form = SaleForm()

    context = {
        'form':form,
        'pen':pen_to_sell
    }
    return render(request, 'financials/sale_form.html', context)

def sale_list(request):
    all_sales = Sale.objects.all().order_by('-date_sold')
    context={
        'sales': all_sales
    }
    return render(request, 'financials/sale_list.html', context)

def dashboard(request):
    # --- 1. Calculate Total Revenue ---
    sales_revenue = Sale.objects.aggregate(
        total=Sum(F('final_sale_price') + F('shipping_charge'))
    )['total'] or Decimal('0.00') # <-- Use Decimal

    # --- 2. Calculate Total Direct Costs for SOLD Pens ---
    sold_pens_pks = Sale.objects.values_list('pen__pk', flat=True)
    
    cost_of_goods_sold = Pen.objects.filter(pk__in=sold_pens_pks).aggregate(
        total=Sum('acquisition_cost')
    )['total'] or Decimal('0.00') # <-- Use Decimal
    
    refurbishment_costs = PenPartsUsage.objects.filter(pen__pk__in=sold_pens_pks).aggregate(
        total=Sum('cost_at_time_of_use')
    )['total'] or Decimal('0.00') # <-- Use Decimal

    sales_shipping_costs = Sale.objects.aggregate(
        total=Sum(F('transaction_fee') + F('other_fees') + F('shipping_cost'))
    )['total'] or Decimal('0.00') # <-- Use Decimal

    # --- 3. Calculate Total General Expenses ---
    general_expenses = Expense.objects.aggregate(total=Sum('cost'))['total'] or Decimal('0.00') # <-- Use Decimal


    TWO_PLACES = Decimal('0.01')
    # --- 4. Final Calculations ---
    gross_profit = (sales_revenue - cost_of_goods_sold).quantize(TWO_PLACES)
    total_business_expenses = (refurbishment_costs + sales_shipping_costs + general_expenses).quantize(TWO_PLACES)
    net_profit = (gross_profit - total_business_expenses).quantize(TWO_PLACES)

    context = {
        'sales_revenue': sales_revenue,
        'gross_profit': gross_profit,
        'total_expenses': total_business_expenses,
        'net_profit': net_profit,
    }
    return render(request, 'financials/dashboard.html', context)
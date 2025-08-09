from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q, Avg

from .models import Expense, Sale
from .forms import ExpenseForm, SaleForm
from inventory.models import Pen, PenPartsUsage
from .utils import get_tax_year_dates

from decimal import Decimal
from collections import defaultdict
from datetime import date, timedelta

import csv
import json

# Create your views here.
@login_required
def expense_list(request):
    all_expenses = Expense.objects.all()
    context = {
        'expenses':all_expenses
    }
    return render(request, 'financials/expense_list.html', context)

@login_required
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

@login_required
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

@login_required
def delete_expense(request, pk):
    expense_to_delete = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense_to_delete.delete()
        return redirect('expense-list')
    
    return redirect('expense-list')

@login_required
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

@login_required
def sale_list(request):

    query = request.GET.get('q')
    sales_queryset = Sale.objects.all().order_by('-date_sold')
    
    if query:
        sales_queryset = sales_queryset.filter(
            Q(pen__pen_model__brand__icontains=query) |
            Q(pen__pen_model__name__icontains=query)
        )
    
    context = {
        'sales': sales_queryset
    }
    return render(request, 'financials/sale_list.html', context)

@login_required
def edit_sale(request, pk):
    sale_to_edit = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale_to_edit)
        if form.is_valid():
            form.save()
            return redirect('sale-list')
    else:
        form = SaleForm(instance=sale_to_edit)
    
    context = {
        'form': form,
        'pen': sale_to_edit.pen
    }
    return render(request, 'financials/sale_form.html', context)

@login_required
def delete_sale(request, pk):
    sale_to_delete = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        pen = sale_to_delete.pen
        #et pen to back instock if deleting the sale record
        pen.status = Pen.STATUS_IN_STOCK
        pen.save()
        
        sale_to_delete.delete()
        return redirect('sale-list')
    
    return redirect('sale-list')

@login_required
def dashboard(request):

    start_date, end_date = get_tax_year_dates()
    
    # Filter sales to only include those within the date range
    sales_this_year = Sale.objects.filter(date_sold__range=(start_date, end_date))
    
    sales_revenue = sales_this_year.aggregate(
        total=Sum(F('final_sale_price') + F('shipping_charge'))
    )['total'] or Decimal('0.00')

    sold_pens_pks = sales_this_year.values_list('pen__pk', flat=True)
    
    cost_of_goods_sold = Pen.objects.filter(pk__in=sold_pens_pks).aggregate(
        total=Sum('acquisition_cost')
    )['total'] or Decimal('0.00')
    
    refurbishment_costs = PenPartsUsage.objects.filter(pen__pk__in=sold_pens_pks).aggregate(
        total=Sum('cost_at_time_of_use')
    )['total'] or Decimal('0.00')

    sales_shipping_costs = sales_this_year.aggregate(
        total=Sum(F('transaction_fee') + F('other_fees') + F('shipping_cost'))
    )['total'] or Decimal('0.00')

    general_expenses = Expense.objects.filter(date_incurred__range=(start_date, end_date)).aggregate(
        total=Sum('cost')
    )['total'] or Decimal('0.00')

    gross_profit = (sales_revenue - cost_of_goods_sold).quantize(Decimal('0.01'))
    total_business_expenses = (refurbishment_costs + sales_shipping_costs + general_expenses).quantize(Decimal('0.01'))
    net_profit = (gross_profit - total_business_expenses).quantize(Decimal('0.01'))

    sales_count = sales_this_year.count()
    avg_profit_per_pen = (net_profit / sales_count) if sales_count > 0 else Decimal('0.00').quantize(Decimal('0.01'))

    current_stock_value = Pen.objects.exclude(status=Pen.STATUS_SOLD).aggregate(
        total=Sum('acquisition_cost')
    )['total'] or Decimal('0.00')

    if net_profit >= 0:
        net_profit_class = 'is-positive'
    else:
        net_profit_class = 'is-negative'

    sales_in_period = Sale.objects.filter(date_sold__range=(start_date, end_date)).select_related('pen')
    expenses_in_period = Expense.objects.filter(date_incurred__range=(start_date, end_date))

    monthly_revenue = defaultdict(Decimal)
    monthly_costs = defaultdict(Decimal)

    for sale in sales_in_period:
        month = sale.date_sold.strftime('%Y-%m')
        
        monthly_revenue[month] += sale.final_sale_price + sale.shipping_charge
        
        pen = sale.pen
        parts_cost = pen.parts_used.aggregate(total=Sum('cost_at_time_of_use'))['total'] or Decimal('0.00')
        total_fees = sale.transaction_fee + sale.other_fees + sale.shipping_cost
        monthly_costs[month] += pen.acquisition_cost + parts_cost + total_fees

    for expense in expenses_in_period:
        month = expense.date_incurred.strftime('%Y-%m')
        monthly_costs[month] += expense.cost

    chart_labels = []
    cumulative_revenue_data = []
    cumulative_profit_data = []
    
    cumulative_revenue = Decimal('0.00')
    cumulative_profit = Decimal('0.00')

    current_date = start_date
    while current_date <= end_date:
        month_key = current_date.strftime('%Y-%m')
        
        cumulative_revenue += monthly_revenue[month_key]
        net_profit_for_month = monthly_revenue[month_key] - monthly_costs[month_key]
        cumulative_profit += net_profit_for_month

        chart_labels.append(current_date.strftime('%b %Y'))
        cumulative_revenue_data.append(cumulative_revenue)
        cumulative_profit_data.append(cumulative_profit)

        next_month = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        current_date = next_month

    total_revenue = cumulative_revenue
    net_profit = cumulative_profit

    context = {
        'tax_year_start': start_date,
        'tax_year_end': end_date,
        'sales_revenue': sales_revenue,
        'gross_profit': gross_profit,
        'total_expenses': total_business_expenses,
        'net_profit': net_profit,
        'net_profit_class': net_profit_class,
        'avg_profit_per_pen': avg_profit_per_pen,
        'current_stock_value': current_stock_value,

        'chart_labels': json.dumps(chart_labels),
        'cumulative_revenue_data': json.dumps([float(d) for d in cumulative_revenue_data]),
        'cumulative_profit_data': json.dumps([float(d) for d in cumulative_profit_data]),
    }
    return render(request, 'financials/dashboard.html', context)

def reports_hub(request):
    sale_dates = Sale.objects.dates('date_sold', 'year')
    expense_dates = Expense.objects.dates('date_incurred', 'year')
    
    all_dates = sorted(list(set(sale_dates) | set(expense_dates)), reverse=True)
    
    tax_years = []
    seen_years = set()
    for dt in all_dates:
        year = dt.year
        if dt.month < 4 or (dt.month == 4 and dt.day < 6):
            tax_year_start = year - 1
        else:
            tax_year_start = year
        
        if tax_year_start not in seen_years:
            tax_years.append(tax_year_start)
            seen_years.add(tax_year_start)

    context = {
        'tax_years': tax_years
    }
    return render(request, 'financials/reports.html', context)


def yearly_report(request, year):
    start_date, end_date = get_tax_year_dates(year)
    
    sales_this_year = Sale.objects.filter(date_sold__range=(start_date, end_date))
    
    sales_revenue = sales_this_year.aggregate(
        total=Sum(F('final_sale_price') + F('shipping_charge'))
    )['total'] or Decimal('0.00')

    sold_pens_pks = sales_this_year.values_list('pen__pk', flat=True)
    
    cost_of_goods_sold = Pen.objects.filter(pk__in=sold_pens_pks).aggregate(
        total=Sum('acquisition_cost')
    )['total'] or Decimal('0.00')
    
    refurbishment_costs = PenPartsUsage.objects.filter(pen__pk__in=sold_pens_pks).aggregate(
        total=Sum('cost_at_time_of_use')
    )['total'] or Decimal('0.00')

    sales_shipping_costs = sales_this_year.aggregate(
        total=Sum(F('transaction_fee') + F('other_fees') + F('shipping_cost'))
    )['total'] or Decimal('0.00')

    general_expenses = Expense.objects.filter(date_incurred__range=(start_date, end_date)).aggregate(
        total=Sum('cost')
    )['total'] or Decimal('0.00')

    gross_profit = (sales_revenue - cost_of_goods_sold).quantize(Decimal('0.01'))
    total_business_expenses = (refurbishment_costs + sales_shipping_costs + general_expenses).quantize(Decimal('0.01'))
    net_profit = (gross_profit - total_business_expenses).quantize(Decimal('0.01'))

    context = {
        'tax_year_start': start_date,
        'tax_year_end': end_date,
        'sales_revenue': sales_revenue,
        'gross_profit': gross_profit,
        'total_expenses': total_business_expenses,
        'net_profit': net_profit,
    }

    return render(request, 'financials/yearly_report.html', context)

def download_sales_csv(request, year):
    start_date, end_date = get_tax_year_dates(year)
    
    filename = f"sales_report_{year}-{year+1}.csv"
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )

    writer = csv.writer(response)
    
    writer.writerow([
        'Date Sold', 'Pen Brand', 'Pen Model', 'Colour', 'Acquisition Cost',
        'Final Sale Price', 'Shipping Charge', 'Transaction Fee', 'Other Fees',
        'Shipping Cost', 'Net Profit'
    ])

    sales = Sale.objects.filter(date_sold__range=(start_date, end_date)).select_related('pen', 'pen__pen_model')

    for sale in sales:
        writer.writerow([
            sale.date_sold,
            sale.pen.pen_model.brand,
            sale.pen.pen_model.name,
            sale.pen.colour,
            sale.pen.acquisition_cost,
            sale.final_sale_price,
            sale.shipping_charge,
            sale.transaction_fee,
            sale.other_fees,
            sale.shipping_cost,
            sale.pen.calculate_net_profit()
        ])

    return response
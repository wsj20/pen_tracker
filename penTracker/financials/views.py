from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q, DecimalField
from django.db.models.functions import Coalesce

from .models import Expense, Sale
from .forms import ExpenseForm, SaleForm
from inventory.models import Pen, PenPartsUsage
from .utils import get_tax_year_dates

from decimal import Decimal
from collections import defaultdict
from datetime import date, timedelta

import csv
import json


@login_required
def expense_list(request):
    all_expenses = Expense.objects.all().order_by('-date_incurred')
    context = {'expenses': all_expenses}
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
        'form': form,
        'pen': pen_to_sell
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
    
    context = {'sales': sales_queryset}
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
        pen.status = Pen.STATUS_IN_STOCK
        pen.save()
        
        sale_to_delete.delete()
        return redirect('sale-list')
    return redirect('sale-list')


@login_required
def dashboard(request):
    start_date, end_date = get_tax_year_dates()
    
    sales_this_year = Sale.objects.filter(date_sold__range=(start_date, end_date))
    sold_pens_pks = sales_this_year.values_list('pen__pk', flat=True)

    # Coalesce database calculations
    gross_turnover = sales_this_year.aggregate(
        total=Coalesce(Sum(F('final_sale_price') + F('shipping_charge')), Decimal('0.00'), output_field=DecimalField())
    )['total']

    cost_of_goods_sold = Pen.objects.filter(pk__in=sold_pens_pks).aggregate(
        total=Coalesce(Sum('acquisition_cost'), Decimal('0.00'), output_field=DecimalField())
    )['total']
    
    refurbishment_costs = PenPartsUsage.objects.filter(pen__pk__in=sold_pens_pks).aggregate(
        total=Coalesce(Sum('cost_at_time_of_use'), Decimal('0.00'), output_field=DecimalField())
    )['total']

    sales_direct_costs = sales_this_year.aggregate(
        total=Coalesce(Sum(F('transaction_fee') + F('other_fees') + F('shipping_cost')), Decimal('0.00'), output_field=DecimalField())
    )['total']

    general_expenses = Expense.objects.filter(date_incurred__range=(start_date, end_date)).aggregate(
        total=Coalesce(Sum('cost'), Decimal('0.00'), output_field=DecimalField())
    )['total']

    allowable_expenses = (cost_of_goods_sold + refurbishment_costs + sales_direct_costs + general_expenses).quantize(Decimal('0.01'))
    net_profit = (gross_turnover - allowable_expenses).quantize(Decimal('0.01'))

    sales_count = sales_this_year.count()
    avg_profit_per_pen = (net_profit / sales_count) if sales_count > 0 else Decimal('0.00')

    # Current Stock Value (excludes SOLD and DONOR pens)
    current_stock_value = Pen.objects.exclude(
        Q(status=Pen.STATUS_SOLD) | Q(status=Pen.STATUS_DONOR)
    ).aggregate(
        total=Coalesce(Sum('acquisition_cost'), Decimal('0.00'), output_field=DecimalField())
    )['total']

    # Estimated Tax Reserve Calculation (NIC Class 4 estimated above £12,570 threshold)
    ni_threshold = Decimal('12570.00')
    taxable_above_threshold = max(Decimal('0.00'), net_profit - ni_threshold)
    tax_reserve_estimate = (taxable_above_threshold * Decimal('0.06')).quantize(Decimal('0.01'))

    # Visual chart analytics
    sales_in_period = sales_this_year.select_related('pen')
    expenses_in_period = Expense.objects.filter(date_incurred__range=(start_date, end_date))

    monthly_turnover = defaultdict(Decimal)
    monthly_profit = defaultdict(Decimal)

    for sale in sales_in_period:
        month = sale.date_sold.strftime('%b %Y')
        turnover = sale.final_sale_price + sale.shipping_charge
        parts_cost = sale.pen.parts_used.aggregate(
            total=Coalesce(Sum('cost_at_time_of_use'), Decimal('0.00'), output_field=DecimalField())
        )['total']
        direct_costs = sale.pen.acquisition_cost + parts_cost + sale.transaction_fee + sale.other_fees + sale.shipping_cost
        
        monthly_turnover[month] += turnover
        monthly_profit[month] += (turnover - direct_costs)

    for expense in expenses_in_period:
        month = expense.date_incurred.strftime('%b %Y')
        monthly_profit[month] -= expense.cost

    chart_labels = list(monthly_turnover.keys())
    chart_turnover = [float(monthly_turnover[m]) for m in chart_labels]
    chart_profit = [float(monthly_profit[m]) for m in chart_labels]

    context = {
        'tax_year_start': start_date,
        'tax_year_end': end_date,
        'gross_turnover': gross_turnover,
        'allowable_expenses': allowable_expenses,
        'net_profit': net_profit,
        'avg_profit_per_pen': avg_profit_per_pen,
        'current_stock_value': current_stock_value,
        'tax_reserve_estimate': tax_reserve_estimate,
        'chart_labels': json.dumps(chart_labels),
        'chart_turnover': json.dumps(chart_turnover),
        'chart_profit': json.dumps(chart_profit),
    }
    return render(request, 'financials/dashboard.html', context)


@login_required
def reports_hub(request):
    sale_dates = Sale.objects.dates('date_sold', 'year')
    expense_dates = Expense.objects.dates('date_incurred', 'year')
    
    all_dates = sorted(list(set(sale_dates) | set(expense_dates)), reverse=True)
    
    tax_years = []
    seen_years = set()
    for dt in all_dates:
        year = dt.year
        tax_year_start = year - 1 if (dt.month < 4 or (dt.month == 4 and dt.day < 6)) else year
        if tax_year_start not in seen_years:
            tax_years.append(tax_year_start)
            seen_years.add(tax_year_start)

    context = {'tax_years': tax_years}
    return render(request, 'financials/reports.html', context)


@login_required
def yearly_report(request, year):
    start_date, end_date = get_tax_year_dates(year)

    if request.GET.get('format') == 'csv':
        return export_sa103s_csv(start_date, end_date, year)
    
    sales_this_year = Sale.objects.filter(date_sold__range=(start_date, end_date))
    
    gross_turnover = sales_this_year.aggregate(
        total=Coalesce(Sum(F('final_sale_price') + F('shipping_charge')), Decimal('0.00'), output_field=DecimalField())
    )['total']

    sold_pens_pks = sales_this_year.values_list('pen__pk', flat=True)
    
    cost_of_goods_sold = Pen.objects.filter(pk__in=sold_pens_pks).aggregate(
        total=Coalesce(Sum('acquisition_cost'), Decimal('0.00'), output_field=DecimalField())
    )['total']
    
    refurbishment_costs = PenPartsUsage.objects.filter(pen__pk__in=sold_pens_pks).aggregate(
        total=Coalesce(Sum('cost_at_time_of_use'), Decimal('0.00'), output_field=DecimalField())
    )['total']

    sales_direct_costs = sales_this_year.aggregate(
        total=Coalesce(Sum(F('transaction_fee') + F('other_fees') + F('shipping_cost')), Decimal('0.00'), output_field=DecimalField())
    )['total']

    general_expenses = Expense.objects.filter(date_incurred__range=(start_date, end_date)).aggregate(
        total=Coalesce(Sum('cost'), Decimal('0.00'), output_field=DecimalField())
    )['total']

    allowable_expenses = (cost_of_goods_sold + refurbishment_costs + sales_direct_costs + general_expenses).quantize(Decimal('0.01'))
    net_profit = (gross_turnover - allowable_expenses).quantize(Decimal('0.01'))

    context = {
        'tax_year_start': start_date,
        'tax_year_end': end_date,
        'gross_turnover': gross_turnover,
        'allowable_expenses': allowable_expenses,
        'net_profit': net_profit,
        'selected_year': year,
    }

    return render(request, 'financials/yearly_report.html', context)


def export_sa103s_csv(start_date, end_date, year):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="SA103S_Summary_{year}-{year+1}.csv"'},
    )

    writer = csv.writer(response)
    
    # SA103S Header Summary
    writer.writerow(['HMRC SA103S Self Assessment (Short) Tax Summary'])
    writer.writerow([f'Tax Year: {start_date} to {end_date}'])
    writer.writerow([])

    sales_this_year = Sale.objects.filter(date_sold__range=(start_date, end_date))
    gross_turnover = sales_this_year.aggregate(
        total=Coalesce(Sum(F('final_sale_price') + F('shipping_charge')), Decimal('0.00'), output_field=DecimalField())
    )['total']

    general_expenses = Expense.objects.filter(date_incurred__range=(start_date, end_date))

    writer.writerow(['Box Name', 'HMRC Field Code', 'Amount (£)'])
    writer.writerow(['Gross Turnover', 'Box 9', gross_turnover])
    
    # Category Expense Breakdown
    for choice_code, choice_label in Expense.HMRC_CATEGORY_CHOICES:
        cat_total = general_expenses.filter(hmrc_category=choice_code).aggregate(
            total=Coalesce(Sum('cost'), Decimal('0.00'), output_field=DecimalField())
        )['total']
        writer.writerow([choice_label, f'Box Expense ({choice_code})', cat_total])

    writer.writerow([])
    writer.writerow(['--- Itemised Sales Ledger ---'])
    writer.writerow(['Date Sold', 'Item Description', 'Sale Price', 'Shipping Charged', 'Platform & Transaction Fees', 'Shipping Cost Net'])

    for sale in sales_this_year.select_related('pen', 'pen__pen_model'):
        writer.writerow([
            sale.date_sold,
            str(sale.pen),
            sale.final_sale_price,
            sale.shipping_charge,
            sale.transaction_fee + sale.other_fees,
            sale.shipping_cost
        ])

    return response
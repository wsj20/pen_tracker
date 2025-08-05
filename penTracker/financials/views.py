from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Sale
from .forms import ExpenseForm

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
from django.shortcuts import render, redirect
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
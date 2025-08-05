from django import forms
from .models import Sale, Expense

class ExpenseForm(forms.ModelForm):
    # Add the date picker widget for the date_incurred field
    date_incurred = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Expense
        fields = ['description', 'date_incurred', 'cost', 'category']

class SaleForm(forms.ModelForm):

    date_sold = forms.DateField(
        widget=forms.DateInput(attrs={'type':'date'})
    )

    class Meta:
        model = Sale
        fields = [
            'date_sold',
            'final_sale_price',
            'shipping_charge',
            'transaction_fee',
            'other_fees',
            'shipping_cost'
        ]
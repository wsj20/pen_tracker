from django import forms
from .models import Pen, PenModel, Supplier

#Main add pen form: /add/
class PenForm(forms.ModelForm):

    #Add date picker
    acquisition_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type':'date'}
        )
    )

    class Meta:
        model = Pen
        fields = [
            'pen_model', 
            'supplier', 
            'colour', 
            'description', 
            'acquisition_cost', 
            'acquisition_date', 
            'status', 
            'ebay_item_id',
            'refurb_note'
        ]

#Add a new pen brand/model
class PenModelForm(forms.ModelForm):
    class Meta:
        model = PenModel
        fields = [
            'brand',
            'name'
        ]

#Add a new supplier
class PenSupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'name',
            'website'
        ]

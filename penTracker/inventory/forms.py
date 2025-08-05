from django import forms
from .models import Pen, PenModel, Supplier

#Main add pen form: /add/
class PenForm(forms.ModelForm):
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

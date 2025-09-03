from django import forms
from .models import Pen, PenModel, Supplier, Part, PenPartsUsage

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

#Part Form
class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = [
            'name',
            'quantity_on_hand',
            'cost_per_unit',
            'description'
        ]

class PenPartUsageForm(forms.ModelForm):

    quantity_used = forms.IntegerField(
        initial=1,
        min_value=1
    )

    class Meta:
        model = PenPartsUsage
        fields = [
            'part',
            'quantity_used'
        ]
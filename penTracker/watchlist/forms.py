from django import forms
from .models import WatchListItem

class WatchListItemForm(forms.ModelForm):
    class Meta:
        model = WatchListItem
        fields = [
            'pen_model',
            'colour',
            'notes'
        ]
from django import forms
from .models import Selection

class SelectionForm(forms.ModelForm):
    class Meta:
        model = Selection
        fields = ['meat_option', 'spicy_level']
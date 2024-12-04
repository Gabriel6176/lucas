from django import forms
from .models import Presupuesto, Item

class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = ['cliente', 'lugar']
        widgets = {
            'cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar': forms.Select(attrs={'class': 'form-control'}),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['cantidad', 'ancho', 'alto', 'tipo', 'color', 'revestimiento']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Cargue el tipo'}),
            'color': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Elija Color'}),
            'revestimiento': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Elija Revestimiento'}),
        }

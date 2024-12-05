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
        fields = ['cantidad', 'ancho', 'alto', 'ancho_hoja', 'tipo', 'color', 'revestimiento', 'desperdicio']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'ancho': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'alto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ancho_hoja': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'revestimiento': forms.Select(attrs={'class': 'form-control'}),
            'desperdicio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'desperdicio': 'Desperdicio (%)',
        }

'''
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['cantidad', 'ancho', 'alto', 'tipo', 'color', 'revestimiento']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'placeholder': 'Ingrese la cantidad'}),
            'ancho': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese el ancho'}),
            'alto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese el alto'}),
            'tipo': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Cargue el tipo'}),
            'color': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Elija Color'}),
            'revestimiento': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Elija Revestimiento'}),
        }
        labels = {
            'cantidad': 'Cantidad',
            'ancho': 'Ancho (cm)',
            'alto': 'Alto (cm)',
            'tipo': 'Tipo',
            'color': 'Color',
            'revestimiento': 'Revestimiento',
        }
'''
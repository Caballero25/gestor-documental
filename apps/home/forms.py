from django import forms
from .models import Module

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['name', 'icon', 'is_visible']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del módulo'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ícono del módulo'}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
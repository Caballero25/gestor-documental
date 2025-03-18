from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Module

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['name', 'icon', 'is_visible']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del módulo'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ícono del módulo [BootsTrap]'}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        error_messages = {
            'name': {
                'unique': _("Ya existe un módulo con este nombre."),
                'required': _("El nombre del módulo es obligatorio."),
            },
            'icon': {
                'unique': _("Este ícono ya está en uso."),
                'required': _("El ícono del módulo es obligatorio."),
            },
        }
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Module, SubModule
from apps.gestor.models import DocumentSequence

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


class SubModuleForm(forms.ModelForm):
    class Meta:
        model = SubModule
        fields = ['name', 'url_name', 'is_visible', 'module']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del submódulo'}),
            'url_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la URL'}),
            'module': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
            }),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        error_messages = {
            'name': {
                'unique': _("Ya existe un submódulo con este nombre."),
                'required': _("El nombre del submódulo es obligatorio."),
            },
            'url_name': {
                'unique': _("Esta URL ya está siendo utilizada en otro submódulo."),
                'required': _("La URL del submódulo es obligatorio."),
            },
            'module': {
                'required': _("El submódulo debe alojarse en un módulo."),
            },
        }

class DocumentSequenceForm(forms.ModelForm):
    class Meta:
        model = DocumentSequence
        fields = ['libro', 'seq_value']
        widgets = {
            'libro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del libro a digitalizar'}),
            'seq_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Inicio de secuencia'}),
        }
        error_messages = {
            'libro': {
                'unique': _("Ya existe un libro con este nombre."),
                'required': _("El nombre del libro es obligatorio."),
            },
            'seq_value': {
                'required': _("La secuencia del libro es obligatoria."),
            },
        }
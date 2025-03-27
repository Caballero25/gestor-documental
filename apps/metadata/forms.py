from django.utils.translation import gettext_lazy as _
from django import forms
from .models import MetadataField, MetadataSchema
import json
class MetadataSchemaForm(forms.ModelForm):
    class Meta:
        model = MetadataSchema
        fields = ['name', 'fields']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del esquema'}),
            'fields': forms.CheckboxSelectMultiple(attrs={'class': ''}),
        }
        error_messages = {
            'name': {
                'unique': _("Este nombre ya está siendo utilizado en otro esquema."),
                'required': _("El nombre del esquema es obligatorio."),
            },
            'fields': {
                'required': _("El necesario establecer los campos del esquema."),
            },
        }



class MetadataFieldEditForm(forms.ModelForm):
    options = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'opcion 1, opcion 2, opcion 3...'}),
        label="Opciones en caso de que el tipo de dato sea 'Selección':",
        required=False
    )
    class Meta:
        model = MetadataField
        fields = ['name', 'field_type', 'options']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del campo'}),
            'field_type': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
            }),
            'options': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'opcion 1, opcion 2, opcion 3...'}),
        }
        error_messages = {
            'name': {
                'unique': _("Este nombre ya está siendo utilizado en otro campo."),
                'required': _("El nombre del campo es obligatorio."),
            },
            'field_type': {
                'required': _("El tipo de campo es obligatorio."),
            },
        }


class MetadataFieldForm(forms.ModelForm):
    options = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'opcion 1, opcion 2, opcion 3...'}),
        label="Opciones en caso de que el tipo de dato sea 'Selección':",
        required=False
    )
    class Meta:
        model = MetadataField
        fields = ['name', 'field_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del campo'}),
            'field_type': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
            }),
        }
        error_messages = {
            'name': {
                'unique': _("Este nombre ya está siendo utilizado en otro campo."),
                'required': _("El nombre del campo es obligatorio."),
            },
            'field_type': {
                'required': _("El tipo de campo es obligatorio."),
            },
        }


    def clean_options(self):
        """Convierte las opciones en formato JSON válido si es un campo select."""
        field_type = self.cleaned_data.get('field_type')
        options = self.cleaned_data.get('options')
        if field_type == 'select' and options:
            options_list = [opt.strip() for opt in options.split(',') if opt.strip()]
            json_options = json.dumps(options_list) 
            print(f"DEBUG - JSON generado: {json_options}")

            return json_options  # Retornar un string JSON válido
        return None  # Si no es select, no se guarda nada
    def save(self, commit=True):
        field = super().save(commit=False) 
        json_options = self.cleaned_data.get('options')
        # Solo asignar si es un campo de selección
        if self.cleaned_data.get('field_type') == 'select':
            field.options = json_options 
        if commit:
            field.save()
        return field
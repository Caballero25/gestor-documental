    
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Document
from ..metadata.models import MetadataSchema, MetadataField
import json

class DocumentAndSchemaForm(forms.ModelForm):
    metadata = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckDefault'}),
    )
    class Meta:
        model = Document 
        fields = ['code_name', 'file', 'metadata_schema']
        widgets = {
            'code_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(?) Opcional: Identificador para buscar el documento posteriormente'}),
            'file': forms.ClearableFileInput(attrs={'class': "form-control", 'id': "formFile"}),
            'metadata_schema': forms.Select(attrs={'class': "form-select"})
        }
        error_messages = {
            'document': {
                'required': _("El documento es obligatorio."),
                'missing': _("No se encontró el archivo en la solicitud."),
            },
        }
    
    
    def clean(self):
        cleaned_data = super().clean()
        metadata = cleaned_data.get("metadata")
        schema = cleaned_data.get("metadata_schema")

        if metadata and schema:
            self.add_error("metadata_schema", "No seleccione un esquema si la opción 'Subir Sin Metadatos' está activada.")
        if not metadata and not schema:
            self.add_error("metadata_schema", "Seleccione un esquema si la opción 'Subir Sin Metadatos' está desactivada.")

        return cleaned_data


class DynamicMetadataForm(forms.Form):
    def __init__(self, *args, **kwargs):
        schema = kwargs.pop('schema', None)
        super(DynamicMetadataForm, self).__init__(*args, **kwargs)

        if schema:
            for field in schema.fields.all():
                if field.field_type == 'text':
                    self.fields[field.name] = forms.CharField(
                        label=field.name, 
                        required=True, 
                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': field.name})
                    )
                elif field.field_type == 'number':
                    self.fields[field.name] = forms.IntegerField(
                        label=field.name, 
                        required=True, 
                        widget=forms.NumberInput(attrs={'class': 'form-control'})
                    )
                elif field.field_type == 'date':
                    self.fields[field.name] = forms.DateField(
                        label=field.name, 
                        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control datepicker-left'})
                    )
                elif field.field_type == 'select':
                    data_str = field.options
                    data_str = data_str.replace('\\"', '"')
                    # Convertir la cadena JSON en una lista de Python
                    data_list = json.loads(data_str)
                    # Crear las opciones del campo select
                    choices = [(option, option) for option in data_list]
                    self.fields[field.name] = forms.ChoiceField(
                        label=field.name, 
                        choices=choices, 
                        widget=forms.Select(attrs={'class': 'form-select'})
                    )
                elif field.field_type == 'checkbox':
                    self.fields[field.name] = forms.BooleanField(
                        label=field.name, 
                        required=False, 
                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                    )
    
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Document
from ..metadata.models import MetadataSchema, MetadataField
import json
from datetime import datetime

#utils
class CustomClearableFileInput(forms.ClearableFileInput):
    initial_text = ""
    input_text = "Cambiar Documento"


#Creación de Document
class DocumentAndSchemaForm(forms.ModelForm):
    metadata = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckDefault'}),
    )
    class Meta:
        model = Document 
        fields = ['code_name', 'file', 'file2', 'metadata_schema']
        widgets = {
            'code_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(?) Opcional: Identificador para buscar el documento posteriormente'}),
            'file': CustomClearableFileInput(attrs={'class': "form-control", 'id': "formFile"}),
            'file2': CustomClearableFileInput(attrs={'class': "form-control", 'id': "formFile2"}),
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



# Edición de document
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['code_name', 'file', 'metadata_schema']
        widgets = {
            'code_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(?) Opcional: Identificador para buscar el documento posteriormente'}),
            'file': CustomClearableFileInput(attrs={'class': "form-control", 'id': "formFile"}),
            'metadata_schema': forms.Select(attrs={'class': "form-select"})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = False  # Hacer el campo de archivo opcional en la edición
# Edición de document
class DynamicFileMetadataForm(forms.Form):
    def __init__(self, *args, **kwargs):
        schema = kwargs.pop('schema', None)
        initial_data = kwargs.pop('initial', {})
        super(DynamicFileMetadataForm, self).__init__(*args, **kwargs)

        if schema:
            for field in schema.fields.all():
                field_name = field.name
                field_value = initial_data.get(field_name, None)
                
                # Configuración común para todos los campos
                field_kwargs = {
                    'label': field.name,
                    'required': False,
                    'initial': field_value,
                }

                if field.field_type == 'text':
                    self.fields[field_name] = forms.CharField(
                        **field_kwargs,
                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': field.name})
                    )
                elif field.field_type == 'number':
                    self.fields[field_name] = forms.IntegerField(
                        **field_kwargs,
                        widget=forms.NumberInput(attrs={'class': 'form-control'})
                    )
                elif field.field_type == 'date':
                    # Convertir string de fecha a objeto date para el campo del formulario
                    if field_value and isinstance(field_value, str):
                        try:
                            field_value = datetime.strptime(field_value, '%Y-%m-%d').date()
                        except (ValueError, TypeError):
                            field_value = None
                    self.fields[field_name] = forms.DateField(
                        **field_kwargs,
                        widget=forms.DateInput(
                            attrs={'type': 'date', 'class': 'form-control datepicker-left'},
                            format='%Y-%m-%d'
                        )
                    )
                elif field.field_type == 'select':
                    choices = []
                    if field.options:
                        if isinstance(field.options, list):
                            choices = [(opt, opt) for opt in field.options]
                        elif isinstance(field.options, str):
                            try:
                                options = json.loads(field.options)
                                choices = [(opt, opt) for opt in options]
                            except json.JSONDecodeError:
                                choices = [(opt.strip(), opt.strip()) for opt in field.options.split(',')]
                    
                    self.fields[field_name] = forms.ChoiceField(
                        **field_kwargs,
                        choices=choices,
                        widget=forms.Select(attrs={'class': 'form-select'})
                    )
                elif field.field_type == 'checkbox':
                    self.fields[field_name] = forms.BooleanField(
                        **field_kwargs,
                        
                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                    )
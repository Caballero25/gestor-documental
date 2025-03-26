    
from django.utils.translation import gettext_lazy as _
from django import forms
from ..metadata.models import MetadataSchema, MetadataField

class DocumentAndSchemaForm(forms.Form):
    code_name = forms.CharField(
        label="Identificador del documento",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(?) Opcional: Identificador para buscar el documento posteriormente'})
    )
    document = forms.FileField(
        label="Seleccionar Documento",
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': "form-control", 'id': "formFile"}),
        error_messages = {
            'required': "El documento es obligatorio.",
            'missing': "No se encontró el archivo en la solicitud.",
        }
    )
    schema = forms.ModelChoiceField(
        queryset=MetadataSchema.objects.all(),
        label="Seleccionar Esquema de Metadatos",
        required=False,
        widget=forms.Select(attrs={'class': "form-select"})
    )
    metadata = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckDefault'}),
    )
    
    def clean(self):
        cleaned_data = super().clean()
        metadata = cleaned_data.get("metadata")
        schema = cleaned_data.get("schema")

        if metadata and schema:
            self.add_error("schema", "No seleccione un esquema si la opción 'Subir Sin Metadatos' está activada.")
        if not metadata and not schema:
            self.add_error("schema", "Seleccione un esquema si la opción 'Subir Sin Metadatos' está desactivada.")

        return cleaned_data




"""
class DynamicMetadataForm(forms.Form):
    def __init__(self, *args, **kwargs):
        schema = kwargs.pop('schema', None)
        super(DynamicMetadataForm, self).__init__(*args, **kwargs)

        if schema:
            for field in schema.fields.all():
                if field.field_type == 'text':
                    self.fields[field.name] = forms.CharField(label=field.name, required=True)
                elif field.field_type == 'number':
                    self.fields[field.name] = forms.IntegerField(label=field.name, required=True)
                elif field.field_type == 'date':
                    self.fields[field.name] = forms.DateField(label=field.name, widget=forms.DateInput(attrs={'type': 'date'}))
                elif field.field_type == 'select':
                    data_str = field.options
                    data_str = data_str.replace('\\"', '"')
                    # Convertir la cadena JSON en una lista de Python
                    data_list = json.loads(data_str)
                    # Mostrar el resultado
                    print(data_list)
                    choices = [(option, option) for option in data_list]
                    self.fields[field.name] = forms.ChoiceField(label=field.name, choices=choices)
                elif field.field_type == 'checkbox':
                    self.fields[field.name] = forms.BooleanField(label=field.name, required=False)"""
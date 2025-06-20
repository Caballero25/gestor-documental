from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Document
from ..metadata.models import MetadataSchema, MetadataField
from .forms import DocumentAndSchemaForm, DynamicMetadataForm
import base64
from django.core.files.base import ContentFile
import uuid
from django.contrib import messages

def capture_document_view(request):
    metadata_schemas = MetadataSchema.objects.all()
    
    if request.method == 'POST':
        form = DocumentAndSchemaForm(request.POST, request.FILES) 
        
        if form.is_valid():
            print("isValid")
            # Crear documento
            document = form.save(commit=False)
            
            if 'file' in request.FILES:
                document.file = request.FILES['file']
            
            document.save()
            print(document)
            
            # Procesar metadatos si es necesario
            if not form.cleaned_data.get('metadata', False) and form.cleaned_data.get('metadata_schema'):
                metadata_schema = form.cleaned_data['metadata_schema']
                metadata_fields = metadata_schema.fields.all()
                metadata_values = {}
                
                for field in metadata_fields:
                    field_name = f"metadata_{field.name}"
                    field_value = request.POST.get(field_name, '')
                    
                    if field_value:
                        if field.field_type == 'checkbox':
                            metadata_values[field.name] = field_value == 'on'
                        else:
                            metadata_values[field.name] = field_value
                
                document.metadata_values = metadata_values
                document.save()
            messages.success(request, 'Documento digitalizado')
            return redirect('capture_document')
        else:
            print(request.POST)
            # Imprimir errores del formulario
            for field, errors in form.errors.items():
                print(f"Campo '{field}':")
                for error in errors:
                    print(f"  - {error}")
            # También puedes imprimir los datos del POST para depuración
    else:
        form = DocumentAndSchemaForm()
    
    return render(request, 'gestor/uploadDocumentImage.html', {
        'metadata_schemas': metadata_schemas,
        'form': form,
    })

def get_metadata_fields(request):
    schema_id = request.GET.get('schema_id')
    if not schema_id:
        return JsonResponse({'error': 'No schema_id provided'}, status=400)
    
    try:
        schema = MetadataSchema.objects.get(id=schema_id)
        fields = list(schema.fields.all().values('name', 'field_type', 'options'))
        return JsonResponse({'fields': fields})
    except MetadataSchema.DoesNotExist:
        return JsonResponse({'error': 'Schema not found'}, status=404)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Document
from ..metadata.models import MetadataSchema
from .forms import DocumentAndSchemaForm, DynamicMetadataForm


def firstSteptUploadView(request):
    context = {}
    context['title'] = 'Paso 1: Seleccionar Documento y Esquema'
    context['breadcrumb_previous'] = "Esquemas"
    context['breadcrumb_previous_link'] = "metadataschema_list"
    if request.method == 'POST':
        form = DocumentAndSchemaForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.cleaned_data.get("file")
            metadata = form.cleaned_data.get("metadata")
            if metadata and document:
                form.save()
                messages.success(request, "Documento subido con éxito")
                return redirect('first-stept-upload') 
            elif not metadata and document:
                record = form.save() 
                record_id = record.id 
                messages.success(request, "Documento listo para adjuntar metadatos")
                return redirect('second-stept-upload', record_id) 
    else:
        form = DocumentAndSchemaForm()
    context['form'] = form
    return render(request, 'gestor/first_stept_create.html', context) 

def secondSteptUploadView(request, id):
    record = get_object_or_404(Document, id=id)
    context = {}
    context['title'] = 'Paso 2: Llenar Metadatos'
    context['breadcrumb_previous'] = "Esquemas"
    context['breadcrumb_previous_link'] = "metadataschema_list"
    context['document_name'] = str(record.file)
    schema = record.metadata_schema
    if request.method == 'POST':
        form = DynamicMetadataForm(request.POST, schema=schema)
        print(1)
        if form.is_valid():
            metadata_values = form.cleaned_data

            for key, value in metadata_values.items():
                if hasattr(value, 'isoformat'):  # Para campos de fecha
                    metadata_values[key] = value.isoformat() # Los otros tipos (str, int, bool) son serializables directamente
                

            record.metadata_values = metadata_values
            record.save()
    else:
        form = DynamicMetadataForm(schema=schema)
        print(record.metadata_schema)
    context['form'] = form
    return render(request, 'gestor/second_stept_create.html', context) 
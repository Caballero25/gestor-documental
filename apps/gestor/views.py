
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Document
from ..metadata.models import MetadataSchema
from .forms import DocumentAndSchemaForm, DynamicMetadataForm, DynamicFileMetadataForm, DocumentForm
from datetime import datetime

def firstSteptUploadView(request, id=None):
    context = {}
    if id:
        record = get_object_or_404(Document, id=id)
        context['record'] = record
        form_get = DocumentAndSchemaForm(instance=record)
        form_post = form = DocumentAndSchemaForm(request.POST, request.FILES, instance=record)
    else:
        form_get = DocumentAndSchemaForm()
        form_post = DocumentAndSchemaForm(request.POST, request.FILES)
    context['title'] = 'Paso 1: Seleccionar Documento y Esquema'
    context['breadcrumb_previous'] = "Esquemas"
    context['breadcrumb_previous_link'] = "metadataschema_list"
    if request.method == 'POST':
        form = form_post
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
        form = form_get
    context['form'] = form
    return render(request, 'gestor/first_stept_create.html', context) 

def secondSteptUploadView(request, id):
    record = get_object_or_404(Document, id=id)
    context = {}
    context['title'] = 'Paso 2: Llenar Metadatos'
    context['breadcrumb_previous'] = "Esquemas"
    context['breadcrumb_previous_link'] = "metadataschema_list"
    context['document'] = record
    schema = record.metadata_schema
    if request.method == 'POST':
        form = DynamicMetadataForm(request.POST, schema=schema)
        if form.is_valid():
            metadata_values = form.cleaned_data

            for key, value in metadata_values.items():
                if hasattr(value, 'isoformat'):  # Para campos de fecha
                    metadata_values[key] = value.isoformat() # Los otros tipos (str, int, bool) son serializables directamente
                

            record.metadata_values = metadata_values
            record.save()
            messages.success(request, "Documento actualizado correctamente")
            return redirect('edit_document_view', id=record.id)
            
    else:
        form = DynamicMetadataForm(schema=schema)
    context['form'] = form
    return render(request, 'gestor/second_stept_create.html', context) 


def editDocumentView(request, id):
    document = get_object_or_404(Document, id=id)
    schema = document.metadata_schema
    print(document)
    
    if request.method == 'POST':
        document_form = DocumentForm(request.POST, request.FILES, instance=document)
        metadata_form = DynamicFileMetadataForm(request.POST, schema=schema, initial=document.metadata_values or {})
        
        if document_form.is_valid() and metadata_form.is_valid():
            # Guardar los datos básicos del documento
            doc = document_form.save()
            
            # Procesar los metadatos
            cleaned_metadata = metadata_form.cleaned_data
            for key, value in cleaned_metadata.items():
                if hasattr(value, 'isoformat'):
                    cleaned_metadata[key] = value.isoformat()
            
            # Actualizar los metadatos manteniendo campos que no están en el formulario
            current_metadata = doc.metadata_values or {}
            doc.metadata_values = {**current_metadata, **cleaned_metadata}
            doc.save()
            
            messages.success(request, "Documento actualizado correctamente")
            return redirect('edit_document_view', id=doc.id)
    else:
        document_form = DocumentForm(instance=document)
        initial_data = document.metadata_values or {}
        if initial_data:
            for key, value in initial_data.items():
                if isinstance(value, str):
                    try:
                        parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
                        initial_data[key] = parsed_date
                    except (ValueError, TypeError):
                        pass
        metadata_form = DynamicFileMetadataForm(schema=schema, initial=initial_data)
    
    return render(request, 'gestor/update_document.html', {
        'document_form': document_form,
        'metadata_form': metadata_form,
        'document': document,
        'schema': schema,
    })
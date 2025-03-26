
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Document
from ..metadata.models import MetadataSchema
from .forms import DocumentAndSchemaForm


def firstSteptUploadView(request):
    context = {}
    context['title'] = 'Paso 1: Seleccionar Documento y Esquema'
    context['breadcrumb_previous'] = "Esquemas"
    context['breadcrumb_previous_link'] = "metadataschema_list"
    if request.method == 'POST':
        form = DocumentAndSchemaForm(request.POST, request.FILES)
        if form.is_valid():
            code_name = form.cleaned_data.get("code_name", "")
            document = form.cleaned_data.get("document")
            schema = form.cleaned_data.get("schema")
            schema = schema.id
            metadata = form.cleaned_data.get("metadata")
            if metadata and document:
                new_document = Document(
                    code_name=code_name,
                    file = document,
                    metadata_schema = None,
                    metadata_values = None
                    )
                new_document.save()
                messages.success(request, "Documento subido con éxito")
                return redirect('first-stept-upload') 

    else:
        form = DocumentAndSchemaForm()
    context['form'] = form
    return render(request, 'gestor/first_stept_create.html', context) 
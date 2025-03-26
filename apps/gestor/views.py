
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
            document = form.cleaned_data.get("file")
            metadata = form.cleaned_data.get("metadata")
            if metadata and document:
                form.save()
                messages.success(request, "Documento subido con éxito")
                return redirect('first-stept-upload') 
            elif not metadata and document:
                form.save()
                messages.success(request, "Documento listo para adjuntar metadatos")
                return redirect('first-stept-upload') 
    else:
        form = DocumentAndSchemaForm()
    context['form'] = form
    return render(request, 'gestor/first_stept_create.html', context) 
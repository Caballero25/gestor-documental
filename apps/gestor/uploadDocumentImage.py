from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Document, DocumentSequence
from ..metadata.models import MetadataSchema, MetadataField
from .forms import DocumentAndSchemaForm, DynamicMetadataForm
import base64
from django.core.files.base import ContentFile
import uuid
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def capture_document_view(request):
    metadata_schemas = MetadataSchema.objects.all()

    if request.method == 'POST':
        form = DocumentAndSchemaForm(request.POST, request.FILES)

        if form.is_valid():
            document = form.save(commit=False)

            if 'file' in request.FILES:
                document.file = request.FILES['file']
            
            document.save()

            if not form.cleaned_data.get('metadata', False) and form.cleaned_data.get('metadata_schema'):
                metadata_schema = form.cleaned_data['metadata_schema']
                metadata_fields = metadata_schema.fields.all()
                metadata_values = {}
                #field_namemetadata_Número de registro - secuencial
                for field in metadata_fields:
                    field_name = f"metadata_{field.name}"
                    field_value = request.POST.get(field_name, '')

                    if field_value:
                        metadata_values[field.name] = field_value == 'on' if field.field_type == 'checkbox' else field_value

                try:
                    secuence = DocumentSequence.objects.get(id=int(request.POST.get('sequence_id')))
                    metadata_values['Número de registro'] = secuence.seq_value
                    secuence.seq_value = secuence.seq_value + 1
                    secuence.save()
                except Exception as e:
                    print("Error en el secuencial")
                document.metadata_values = metadata_values
                document.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                messages.success(request, 'Documento digitalizado')
                return redirect('capture_document')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    else:
        form = DocumentAndSchemaForm()
    secuenciales = DocumentSequence.objects.filter().all()

    return render(request, 'gestor/uploadDocumentImage.html', {
        'metadata_schemas': metadata_schemas,
        'form': form,
        'secuenciales': secuenciales
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
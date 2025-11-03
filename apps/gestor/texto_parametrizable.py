from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import TextoParametrizable, MetadataSchema
from .forms import TextoParametrizableForm

def texto_parametrizable_list(request):
    """
    Vista para listar todos los textos parametrizables
    """
    textos = TextoParametrizable.objects.all().select_related('schema')
    esquemas = MetadataSchema.objects.all().values('id', 'name')

    return render(request, 'metadata/texto_parametrizable/crud.html', {'textos': textos, 'esquemas': list(esquemas)})

@csrf_exempt
@require_http_methods(["POST"])
def texto_parametrizable_create(request):
    """
    Vista para crear un nuevo texto parametrizable (AJAX)
    """
    try:
        data = json.loads(request.body)
        form = TextoParametrizableForm(data)
        
        if form.is_valid():
            texto = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Texto parametrizable creado exitosamente.',
                'data': {
                    'id': texto.id,
                    'schema_name': texto.schema.name,
                    'plantilla_texto': texto.plantilla_texto
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Error en el formulario.',
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def texto_parametrizable_update(request, pk):
    """
    Vista para actualizar un texto parametrizable (AJAX)
    """
    try:
        texto = get_object_or_404(TextoParametrizable, pk=pk)
        data = json.loads(request.body)
        form = TextoParametrizableForm(data, instance=texto)
        
        if form.is_valid():
            texto = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Texto parametrizable actualizado exitosamente.',
                'data': {
                    'id': texto.id,
                    'schema_name': texto.schema.name,
                    'plantilla_texto': texto.plantilla_texto
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Error en el formulario.',
                'errors': form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["DELETE"])
def texto_parametrizable_delete(request, pk):
    """
    Vista para eliminar un texto parametrizable (AJAX)
    """
    try:
        texto = get_object_or_404(TextoParametrizable, pk=pk)
        schema_name = texto.schema.name
        texto.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Texto parametrizable para "{schema_name}" eliminado exitosamente.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        })

def texto_parametrizable_detail(request, pk):
    """
    Vista para obtener los detalles de un texto parametrizable (AJAX)
    """
    try:
        texto = get_object_or_404(TextoParametrizable, pk=pk)
        return JsonResponse({
            'success': True,
            'data': {
                'id': texto.id,
                'schema': texto.schema.id,
                'schema_name': texto.schema.name,
                'plantilla_texto': texto.plantilla_texto
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        })
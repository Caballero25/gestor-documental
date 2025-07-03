from django.http import JsonResponse
from .models import DocumentSequence
from django.views.decorators.csrf import csrf_exempt
import json

# Inicializar si no existe
def get_or_create_sequence():
    seq_obj, created = DocumentSequence.objects.get_or_create(id=1, defaults={'seq_value': 1})
    return seq_obj

# Obtener el valor actual de la secuencia
def getSeqValue(request):
    seq_obj = get_or_create_sequence()
    return JsonResponse({'success': True, 'seq_value': seq_obj.seq_value})

# Establecer un nuevo valor para la secuencia (solo POST)
@csrf_exempt
def setSeqValue(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_value = int(data.get('seq_value', 0))
            if new_value < 0:
                return JsonResponse({'success': False, 'error': 'El valor debe ser positivo'}, status=400)
            seq_obj = get_or_create_sequence()
            seq_obj.seq_value = new_value
            seq_obj.save()
            return JsonResponse({'success': True, 'seq_value': seq_obj.seq_value})
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({'success': False, 'error': 'JSON inválido o valor incorrecto'}, status=400)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

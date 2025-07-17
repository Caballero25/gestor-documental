from django.http import JsonResponse
from .models import DocumentSequence
from django.views.decorators.csrf import csrf_exempt
import json


# Obtener el valor actual de la secuencia
def getSeqValue(request):
    try:
        id = request.GET.get("id")
        if not id:
            return JsonResponse({'success': False, 'error': 'ID no proporcionado'}, status=400)
            
        sequence = DocumentSequence.objects.get(id=int(id))
        return JsonResponse({'success': True, 'seq_value': sequence.seq_value})
    except DocumentSequence.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Secuencia no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# Establecer un nuevo valor para la secuencia (solo POST)
@csrf_exempt
def setSeqValue(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            new_value = int(data.get('seq_value', 0))
            
            if not id:
                return JsonResponse({'success': False, 'error': 'ID no proporcionado'}, status=400)
                
            if new_value < 0:
                return JsonResponse({'success': False, 'error': 'El valor debe ser positivo'}, status=400)

            sequence = DocumentSequence.objects.get(id=int(id))
            sequence.seq_value = new_value
            sequence.save()
            return JsonResponse({'success': True, 'seq_value': sequence.seq_value})
        except DocumentSequence.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Secuencia no encontrada'}, status=404)
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({'success': False, 'error': 'JSON inválido o valor incorrecto'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
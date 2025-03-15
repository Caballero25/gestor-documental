from .models import Module  

def modulos_sistema(request):
    modulos_sistema = Module.objects.filter(is_visible=True).order_by('name')  # Ordenado alfabéticamente
    return {
        'modulos_sistema': modulos_sistema
    }
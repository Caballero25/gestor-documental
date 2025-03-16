from django.shortcuts import render
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView
from .models import Module

# Create your views here.
@login_required
def home(request):
    return render(request, "home/home.html")

class ModuleListView(LoginRequiredMixin, ListView):
    model = Module
    template_name = 'parametrization/modules/module_list.html'
    permission_required = 'view_module'
    paginate_by = 10  

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)  # Ajusta el campo de búsqueda
        return queryset

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Módulos'
        context['parametroBusqueda'] = 'Nombre'
        context['query'] = self.request.GET.get('q', '')
        context['delete_url'] = "module_delete"
        return context

@permission_required("delete_module")    
def moduleDeleteView(request, id):
    record = Module.objects.get(id=id) 
    context = {}
    context['title'] = 'Eliminar Módulo'
    context['record'] = record
    if request.method == 'POST':
        try:
            record.delete()
            return JsonResponse({"status": True}, status=HTTPStatus.NO_CONTENT)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)


    return render(request, 'parametrization/modules/module_delete.html', context)
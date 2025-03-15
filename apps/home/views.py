from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Module

# Create your views here.
@login_required
def home(request):
    return render(request, "home/home.html")

class ModuleListView(LoginRequiredMixin, ListView):
    model = Module
    template_name = 'home/module.html'
    permission_required = 'view_module'
    paginate_by = 10  # Número de elementos por página

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
        return context
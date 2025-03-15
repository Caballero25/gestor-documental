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

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Módulos'
        return context
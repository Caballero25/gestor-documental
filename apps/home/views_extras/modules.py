
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView
from ..models import Module
from ..forms import ModuleForm
class ModuleListView(PermissionRequiredMixin, ListView):
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
        context['create_url'] = "module_create"
        context['delete_url'] = "module_delete"
        context['update_url'] = "module_edit"
        context['breadcrumb_previous'] = "Inicio"
        context['breadcrumb_previous_link'] = "home-url"
        return context

@permission_required("add_module")
def moduleCreateView(request):
    context = {}
    context['title'] = 'Crear Módulo'
    context['breadcrumb_previous'] = "Módulos"
    context['breadcrumb_previous_link'] = "module_list"
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('module_list')  # Redirige a la lista de módulos
    else:
        form = ModuleForm()
    context['form'] = form
    return render(request, 'parametrization/modules/module_create.html', context) 

@permission_required("change_module")
def moduleUpdateView(request, id):
    record = get_object_or_404(Module, id=id)
    context = {}
    context['title'] = 'Editar Módulo'
    context['record'] = record
    context['breadcrumb_previous'] = "Módulos"
    context['breadcrumb_previous_link'] = "module_list"
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('module_list')  # Redirige a una vista de listado de módulos
    else:
        form = ModuleForm(instance=record)
    context['form'] = form
    return render(request, 'parametrization/modules/module_edit.html', context)


@permission_required("delete_module")
def moduleDeleteView(request, id):
    record = Module.objects.get(id=id) 
    context = {}
    context['title'] = 'Eliminar Módulo'
    context['record'] = record
    context['breadcrumb_previous'] = "Módulos"
    context['breadcrumb_previous_link'] = "module_list"
    context['success_redirection'] = "module_list"
    if request.method == 'POST':
        try:
            record.delete()
            return JsonResponse({"status": True}, status=HTTPStatus.NO_CONTENT)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
    return render(request, 'parametrization/modules/module_delete.html', context)
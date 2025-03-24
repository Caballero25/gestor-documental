
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView
from ..models import SubModule
from ..forms import SubModuleForm
class SubModuleListView(PermissionRequiredMixin, ListView):
    model = SubModule
    template_name = 'parametrization/submodules/submodule_list.html'
    permission_required = 'view_submodule'
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
        context['title'] = 'Listado de Submódulos'
        context['parametroBusqueda'] = 'Nombre'
        context['query'] = self.request.GET.get('q', '')
        context['create_url'] = "submodule_create"
        context['delete_url'] = "submodule_delete"
        context['update_url'] = "submodule_edit"
        context['breadcrumb_previous'] = "Inicio"
        context['breadcrumb_previous_link'] = "home-url"
        return context

@permission_required("add_submodule")
def subModuleCreateView(request):
    context = {}
    context['title'] = 'Crear Submódulo'
    context['breadcrumb_previous'] = "Submódulos"
    context['breadcrumb_previous_link'] = "submodule_list"
    if request.method == 'POST':
        form = SubModuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('submodule_list')  # Redirige a la lista de módulos
    else:
        form = SubModuleForm()
    context['form'] = form
    return render(request, 'parametrization/submodules/submodule_create.html', context) 

@permission_required("change_submodule")
def subModuleUpdateView(request, id):
    record = get_object_or_404(SubModule, id=id)
    context = {}
    context['title'] = 'Editar Submódulo'
    context['record'] = record
    context['breadcrumb_previous'] = "Submódulos"
    context['breadcrumb_previous_link'] = "submodule_list"
    if request.method == 'POST':
        form = SubModuleForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('submodule_list')  # Redirige a una vista de listado de módulos
    else:
        form = SubModuleForm(instance=record)
    context['form'] = form
    return render(request, 'parametrization/submodules/submodule_edit.html', context)


@permission_required("delete_submodule")
def subModuleDeleteView(request, id):
    record = SubModule.objects.get(id=id) 
    context = {}
    context['title'] = 'Eliminar Submódulo'
    context['record'] = record
    context['breadcrumb_previous'] = "Submódulos"
    context['breadcrumb_previous_link'] = "submodule_list"
    context['success_redirection'] = "submodule_list"
    if request.method == 'POST':
        try:
            record.delete()
            return JsonResponse({"status": True}, status=HTTPStatus.NO_CONTENT)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
    return render(request, 'parametrization/submodules/submodule_delete.html', context)
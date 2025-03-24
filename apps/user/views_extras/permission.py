
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth.models import Permission
from ..forms import PermissionForm
class PermissionListView(LoginRequiredMixin, ListView):
    model = Permission
    template_name = 'auth/permission/permission_list.html'
    permission_required = 'view_permission'
    paginate_by = 10  

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(codename__icontains=query))  # Ajusta el campo de búsqueda
        return queryset

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Permisos'
        context['parametroBusqueda'] = 'Nombre o Código'
        context['query'] = self.request.GET.get('q', '')
        context['create_url'] = "permission_create"
        context['delete_url'] = "permission_delete"
        context['update_url'] = "permission_edit"
        context['breadcrumb_previous'] = "Inicio"
        context['breadcrumb_previous_link'] = "home-url"
        return context

@permission_required("add_permission")
def permissionCreateView(request):
    context = {}
    context['title'] = 'Crear Permiso'
    context['breadcrumb_previous'] = "Permisos"
    context['breadcrumb_previous_link'] = "permission_list"
    if request.method == 'POST':
        form = PermissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            #form.save_m2m()
            return redirect('permission_list')  # Redirige a la lista de módulos
    else:
        form = PermissionForm()
    context['form'] = form
    return render(request, 'auth/permission/permission_create.html', context) 

@permission_required("change_permission")
def permissionUpdateView(request, id):
    record = get_object_or_404(Permission, id=id)
    context = {}
    context['title'] = 'Editar Permiso'
    context['record'] = record
    context['breadcrumb_previous'] = "Permisos"
    context['breadcrumb_previous_link'] = "permission_list"
    if request.method == 'POST':
        form = PermissionForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            #form.save_m2m()  # Guarda las relaciones ManyToMany (grupos)
            return redirect('permission_list') 
    else:
        form = PermissionForm(instance=record)
    context['form'] = form
    return render(request, 'auth/permission/permission_edit.html', context)


@permission_required("delete_permission")
def permissionDeleteView(request, id):
    record = Permission.objects.get(id=id) 
    context = {}
    context['title'] = 'Eliminar Permiso'
    context['record'] = record
    context['breadcrumb_previous'] = "Permisos"
    context['breadcrumb_previous_link'] = "permission_list"
    context['success_redirection'] = "permission_list"
    if request.method == 'POST':
        try:
            record.delete()
            return JsonResponse({"status": True}, status=HTTPStatus.NO_CONTENT)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
    return render(request, 'auth/permission/permission_delete.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth.models import Group
from ..forms import GroupForm
class GroupListView(PermissionRequiredMixin, ListView):
    model = Group
    template_name = 'auth/group/group_list.html'
    permission_required = 'view_group'
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
        context['title'] = 'Listado de Grupos'
        context['parametroBusqueda'] = 'Nombre'
        context['query'] = self.request.GET.get('q', '')
        context['create_url'] = "group_create"
        context['delete_url'] = "group_delete"
        context['update_url'] = "group_edit"
        context['breadcrumb_previous'] = "Inicio"
        context['breadcrumb_previous_link'] = "home-url"
        return context

@permission_required("add_group")
def groupCreateView(request):
    context = {}
    context['title'] = 'Crear Grupo'
    context['breadcrumb_previous'] = "Grupos"
    context['breadcrumb_previous_link'] = "group_list"
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            #form.save_m2m()
            return redirect('group_list')  # Redirige a la lista de módulos
    else:
        form = GroupForm()
    context['form'] = form
    return render(request, 'auth/group/group_create.html', context) 

@permission_required("change_group")
def groupUpdateView(request, id):
    record = get_object_or_404(Group, id=id)
    context = {}
    context['title'] = 'Editar Grupo'
    context['record'] = record
    context['breadcrumb_previous'] = "Grupos"
    context['breadcrumb_previous_link'] = "group_list"
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            #form.save_m2m()  # Guarda las relaciones ManyToMany (grupos)
            return redirect('group_list') 
    else:
        form = GroupForm(instance=record)
    context['form'] = form
    return render(request, 'auth/group/group_edit.html', context)


@permission_required("delete_group")
def groupDeleteView(request, id):
    record = Group.objects.get(id=id) 
    context = {}
    context['title'] = 'Eliminar Grupo'
    context['record'] = record
    context['breadcrumb_previous'] = "Grupos"
    context['breadcrumb_previous_link'] = "group_list"
    context['success_redirection'] = "group_list"
    if request.method == 'POST':
        try:
            record.delete()
            return JsonResponse({"status": True}, status=HTTPStatus.NO_CONTENT)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
    return render(request, 'auth/group/group_delete.html', context)
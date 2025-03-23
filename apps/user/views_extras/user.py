
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.views.generic import ListView
from ..models import User
from ..forms import UserForm
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'auth/user/user_list.html'
    permission_required = 'view_user'
    paginate_by = 10  

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(username__icontains=query) | Q(email__icontains=query))  # Ajusta el campo de búsqueda
        return queryset

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Usuarios'
        context['parametroBusqueda'] = 'Nombre o Correo Electrónico'
        context['query'] = self.request.GET.get('q', '')
        context['create_url'] = "module_create"
        context['delete_url'] = "user_delete"
        context['update_url'] = "user_edit"
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
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('module_list')  # Redirige a la lista de módulos
    else:
        form = UserForm()
    context['form'] = form
    return render(request, 'parametrization/modules/module_create.html', context) 

@permission_required("change_user")
def userUpdateView(request, id):
    record = get_object_or_404(User, id=id)
    context = {}
    context['title'] = 'Editar Usuario'
    context['record'] = record
    context['breadcrumb_previous'] = "Usuarios"
    context['breadcrumb_previous_link'] = "user_list"
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            return redirect('user_list')  # Redirige a una vista de listado de módulos
    else:
        form = UserForm(instance=record)
    context['form'] = form
    return render(request, 'auth/user/user_edit.html', context)


@permission_required("delete_user")
def userDeleteView(request, id):
    record = User.objects.get(id=id) 
    context = {}
    context['title'] = 'Eliminar Usuario'
    context['record'] = record
    context['breadcrumb_previous'] = "Usuarios"
    context['breadcrumb_previous_link'] = "user_list"
    context['success_redirection'] = "user_list"
    if request.method == 'POST':
        try:
            record.delete()
            return JsonResponse({"status": True}, status=HTTPStatus.NO_CONTENT)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
    return render(request, 'auth/user/user_delete.html', context)
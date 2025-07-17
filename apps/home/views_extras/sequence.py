
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView
from apps.gestor.models import DocumentSequence
from ..forms import DocumentSequenceForm
class SequenceListView(ListView):
    model = DocumentSequence
    template_name = 'parametrization/secuenciales/secuencial_list.html'
    paginate_by = 10  

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(libro__icontains=query)  # Ajusta el campo de búsqueda
        return queryset

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de secuenciales'
        context['parametroBusqueda'] = 'Nombre de libro'
        context['query'] = self.request.GET.get('q', '')
        context['create_url'] = "sequence_create"
        context['delete_url'] = "sequence_delete"
        context['update_url'] = "sequence_edit"
        context['breadcrumb_previous'] = "Inicio"
        context['breadcrumb_previous_link'] = "home-url"
        return context

def sequenceCreateView(request):
    context = {}
    context['title'] = 'Crear secuencia'
    context['breadcrumb_previous'] = "Secuenciales"
    context['breadcrumb_previous_link'] = "sequence_list"
    if request.method == 'POST':
        form = DocumentSequenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sequence_list')  # Redirige a la lista de módulos
    else:
        form = DocumentSequenceForm()
    context['form'] = form
    return render(request, 'parametrization/secuenciales/secuencial_create.html', context) 

def sequenceUpdateView(request, id):
    record = get_object_or_404(DocumentSequence, id=id)
    context = {}
    context['title'] = 'Editar secuencial'
    context['record'] = record
    context['breadcrumb_previous'] = "Secuenciales"
    context['breadcrumb_previous_link'] = "sequence_list"
    if request.method == 'POST':
        form = DocumentSequenceForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('sequence_list')  # Redirige a una vista de listado de módulos
    else:
        form = DocumentSequenceForm(instance=record)
    context['form'] = form
    return render(request, 'parametrization/secuenciales/secuencial_edit.html', context)

def sequenceDeleteView(request, id):
    record = DocumentSequence.objects.get(id=id) 
    context = {}
    context['title'] = 'Eliminar secuencial'
    context['record'] = record
    context['breadcrumb_previous'] = "Secuenciales"
    context['breadcrumb_previous_link'] = "sequence_list"
    context['success_redirection'] = "sequence_list"
    if request.method == 'POST':
        try:
            record.delete()
            return JsonResponse({"status": True}, status=HTTPStatus.NO_CONTENT)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
    return render(request, 'parametrization/secuenciales/secuencial_delete.html', context)
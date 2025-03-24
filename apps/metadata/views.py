
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.views.generic import ListView
from .models import MetadataSchema, MetadataField
from .forms import MetadataSchemaForm, MetadataFieldForm, MetadataFieldEditForm

#   SCHEMA
class MetaDataSchemaListView(PermissionRequiredMixin, ListView):
    model = MetadataSchema
    template_name = 'metadata/schema/schema_list.html'
    permission_required = 'view_metadataschema'
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
        context['title'] = 'Listado de Esquemas de Metadatos'
        context['parametroBusqueda'] = 'Nombre'
        context['query'] = self.request.GET.get('q', '')
        context['create_url'] = "metadataschema_create"
        context['delete_url'] = "metadataschema_delete"
        context['update_url'] = "metadataschema_edit"
        context['breadcrumb_previous'] = "Inicio"
        context['breadcrumb_previous_link'] = "home-url"
        return context

@permission_required("add_metadataschema")
def metaDataSchemaCreateView(request):
    context = {}
    context['title'] = 'Crear Esquema de Metadatos'
    context['breadcrumb_previous'] = "Esquemas"
    context['breadcrumb_previous_link'] = "metadataschema_list"
    if request.method == 'POST':
        form = MetadataSchemaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            #form.save_m2m()
            return redirect('metadataschema_list')  # Redirige a la lista de módulos
    else:
        form = MetadataSchemaForm()
    context['form'] = form
    return render(request, 'metadata/schema/schema_create.html', context) 

@permission_required("change_metadataschema")
def metaDataSchemaUpdateView(request, id):
    record = get_object_or_404(MetadataSchema, id=id)
    context = {}
    context['title'] = 'Editar Esquema de Metadatos'
    context['record'] = record
    context['breadcrumb_previous'] = "Esquemas"
    context['breadcrumb_previous_link'] = "metadataschema_list"
    if request.method == 'POST':
        form = MetadataSchemaForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            #form.save_m2m()  # Guarda las relaciones ManyToMany (grupos)
            return redirect('metadataschema_list') 
    else:
        form = MetadataSchemaForm(instance=record)
    context['form'] = form
    return render(request, 'metadata/schema/schema_edit.html', context)


@permission_required("delete_metadataschema")
def metaDataSchemaDeleteView(request, id):
    record = MetadataSchema.objects.get(id=id) 
    context = {}
    context['title'] = 'Eliminar Esquema de Metadatos'
    context['record'] = record
    context['breadcrumb_previous'] = "Esquemas"
    context['breadcrumb_previous_link'] = "metadataschema_list"
    context['success_redirection'] = "metadataschema_list"
    if request.method == 'POST':
        try:
            record.delete()
            return JsonResponse({"status": True}, status=HTTPStatus.NO_CONTENT)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
    return render(request, 'metadata/schema/schema_delete.html', context)


#   FIELD
class MetaDataFieldListView(PermissionRequiredMixin, ListView):
    model = MetadataField
    template_name = 'metadata/field/field_list.html'
    permission_required = 'view_metadatafield'
    paginate_by = 10  

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(field_type__icontains=query))  # Ajusta el campo de búsqueda
        return queryset

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Campos'
        context['parametroBusqueda'] = 'Nombre o Tipo de Dato'
        context['query'] = self.request.GET.get('q', '')
        context['create_url'] = "metadatafield_create"
        context['delete_url'] = "metadatafield_delete"
        context['update_url'] = "metadatafield_edit"
        context['breadcrumb_previous'] = "Inicio"
        context['breadcrumb_previous_link'] = "home-url"
        return context

@permission_required("add_metadatafield")
def metaDataFieldCreateView(request):
    context = {}
    context['title'] = 'Crear Campo'
    context['breadcrumb_previous'] = "Campos de Esquema"
    context['breadcrumb_previous_link'] = "metadatafield_list"
    if request.method == 'POST':
        form = MetadataFieldForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            #form.save_m2m()
            return redirect('metadatafield_list')  # Redirige a la lista de módulos
    else:
        form = MetadataFieldForm()
    context['form'] = form
    return render(request, 'metadata/field/field_create.html', context) 

@permission_required("change_metadatafield")
def metaDataFieldUpdateView(request, id):
    record = get_object_or_404(MetadataField, id=id)
    context = {}
    context['title'] = 'Editar Campo'
    context['record'] = record
    context['breadcrumb_previous'] = "Campos de Esquema"
    context['breadcrumb_previous_link'] = "metadatafield_list"
    if request.method == 'POST':
        form = MetadataFieldEditForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            form.save()
            #form.save_m2m()  # Guarda las relaciones ManyToMany (grupos)
            return redirect('metadatafield_list') 
    else:
        form = MetadataFieldEditForm(instance=record)
    context['form'] = form
    return render(request, 'metadata/field/field_edit.html', context)


@permission_required("delete_metadatafield")
def metaDataFieldDeleteView(request, id):
    record = MetadataField.objects.get(id=id) 
    context = {}
    context['title'] = 'Eliminar Campo'
    context['record'] = record
    context['breadcrumb_previous'] = "Campos de Esquema"
    context['breadcrumb_previous_link'] = "metadatafield_list"
    context['success_redirection'] = "metadatafield_list"
    if request.method == 'POST':
        try:
            record.delete()
            return JsonResponse({"status": True}, status=HTTPStatus.NO_CONTENT)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
    return render(request, 'metadata/field/field_delete.html', context)
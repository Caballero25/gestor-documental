from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Document

def sendDocumentLink(request, id):
    context = {}
    context['title'] = 'Enviar Documentos - Correo Electrónico'
    context['breadcrumb_previous'] = "Documentos"
    context['breadcrumb_previous_link'] = "document_list"
    return render(request, 'gestor/send_document_email.html', context)


@login_required
def search_documents(request):
    query = request.GET.get('q', '')
    if query:
        filters = Q(code_name__icontains=query) | Q(file__icontains=query)
        # Verificar si query es un número antes de aplicarlo al campo 'id'
        if query.isdigit():
            filters |= Q(id=int(query))
        documents = Document.objects.filter(filters)
        data = [{"id": u.id, "code_name": u.code_name, "name": str(u.file)} for u in documents]
    else:
        data = []
    return JsonResponse({"documents": data})
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .models import Document

def sendDocumentLink(request, id):
    context = {}
    context['title'] = 'Enviar Documentos - Correo Electrónico'
    context['breadcrumb_previous'] = "Documentos"
    context['breadcrumb_previous_link'] = "document_list"
    return render(request, 'gestor/send_document_email.html', context)


@login_required
def searchDocuments(request):
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

def sendEmailDocuments(request):
    if request.method == 'POST':
        asunto = request.POST.get("asunto")
        cuerpo = request.POST.get("cuerpo")

        # Obtener todos los correos y documentos como listas
        added_emails = request.POST.getlist("addedEmails[]")  
        added_documents = request.POST.getlist("addedDocuments[]")  

        print("Asunto:", asunto)
        print("Cuerpo:", cuerpo)
        print("Added Emails:", added_emails)
        print("Added Documents:", added_documents)

        return JsonResponse({"message": "Correo enviado correctamente", "emails": added_emails, "documents": added_documents})

    return JsonResponse({"error": "Método no permitido"}, status=405)
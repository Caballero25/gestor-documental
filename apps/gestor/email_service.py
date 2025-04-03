from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
        signer = TimestampSigner()
        enlaces_documentos = []
        asunto = request.POST.get("asunto")
        cuerpo = request.POST.get("cuerpo")
        enlaces = ""

        # Obtener todos los correos y documentos como listas
        added_emails = request.POST.getlist("addedEmails[]")  
        added_documents = request.POST.getlist("addedDocuments[]")  

        #Creamos el enlace de descarga temporal para el documento | 7 días
        for documento in added_documents:
            record = get_object_or_404(Document, id=int(documento))
            token = signer.sign(record.id)
            enlaces_documentos.append(f"{token}")
        for enlace in enlaces_documentos:
            url_relativa = reverse('download_documents', kwargs={'token': enlace})
            url_completa = request.build_absolute_uri(url_relativa)
            enlaces += f"\n<p>Descargar el documento en este enlace: <a href={url_completa}>{url_completa}</a>.</p> "
        mensaje_html = f"""
                                <html>
                                <head></head>
                                <body>
                                    <p>{cuerpo}.</p>
                                    {enlaces}
                                </body>
                                </html>
                            """
        sendEmail(asunto, mensaje_html, added_emails)
        return JsonResponse({"message": "Correo enviado correctamente", "emails": added_emails, "documents": added_documents})

    return JsonResponse({"error": "Método no permitido"}, status=405)

def downloadDocument(request, token):
    try:
        signer = TimestampSigner()
        doc_id = signer.unsign(token, max_age=int(settings.LINK_EXPIRATION))  # 7 días en segundos
        documento = get_object_or_404(Document, pk=doc_id)
        return HttpResponse("Este enlace es bueno", status=200)
    except SignatureExpired:
        return HttpResponse("Este enlace ha expirado", status=410)
    except BadSignature:
        return HttpResponse("Enlace inválido", status=404)

def sendEmail(subject, body, added_emails: list):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = ", ".join(added_emails)  # Convertir la lista en una cadena
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    # Conectar con el servidor SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    # Enviar el correo
    server.sendmail(settings.EMAIL_HOST_USER, added_emails, msg.as_string())

    # Cerrar la conexión
    server.quit()
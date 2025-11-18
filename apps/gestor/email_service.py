from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.urls import reverse
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .models import Document
import os

def sendDocumentLink(request):
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
        sended_emails = sendEmail(asunto, mensaje_html, added_emails)    
        return JsonResponse({"message": "Correo enviado correctamente", "emails": sended_emails, "documents": added_documents})

    return JsonResponse({"error": "Método no permitido"}, status=405)

def downloadDocument(request, token):
    try:
        signer = TimestampSigner()
        doc_id = signer.unsign(token, max_age=int(settings.LINK_EXPIRATION))  # 7 días en segundos
        documento = get_object_or_404(Document, pk=doc_id)
        file_name = os.path.basename(documento.file.path)
        # Abre el archivo en modo binario
        file = open(documento.file.path, 'rb')
        
        # Crea la respuesta con el archivo
        response = FileResponse(file)
        
        # Configura los headers para forzar la descarga
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response['Content-Type'] = 'application/octet-stream'
        
        return response
    except SignatureExpired:
        context = {
            "title": "¡Enlace expirado!",
            "body": "El enlace que has utilizado para acceder al documento ha expirado. Por motivos de seguridad, los enlaces de descarga tienen un tiempo limitado de validez."
        }
        return render(request, 'gestor/invalid_link.html', context)
        #return HttpResponse("Este enlace ha expirado", status=410)
    except BadSignature:
        return HttpResponse("Enlace inválido", status=404)
    except:
        context = {
            "title": "¡Algo salió mal!",
            "body": "El enlace que has utilizado para acceder al documento no ha funcionado."
        }
        return render(request, 'gestor/invalid_link.html', context)
    
#DESDE PDF PARAMETRIZABLE
@csrf_exempt
def sendEmailPdf(request):
    if request.method == 'POST':
        signer = TimestampSigner()
        asunto = request.POST.get("asunto")
        cuerpo = request.POST.get("cuerpo") if request.POST.get("cuerpo") else ""
        
        # 1. Recibimos los datos según tu nuevo requerimiento
        # Asumo que enviarás 'main_email' como string y 'cc_emails' como lista desde el front
        main_email = request.POST.get("main_email") 
        cc_emails = request.POST.getlist("cc_emails[]") # Lista de copias
        document_id = request.POST.get("document_id")   # Un solo ID

        # Validaciones básicas
        if not main_email or not document_id:
            return JsonResponse({"error": "Faltan datos obligatorios (email o documento)"}, status=400)

        # 2. Procesamos EL documento único
        # Buscamos el documento. Si no existe, devuelve 404 automáticamente.
        record = get_object_or_404(Document, id=int(document_id))
        
        # Generamos el token firmado para este documento específico
        token = signer.sign(record.id)
        
        # Creamos la URL absoluta
        url_relativa = reverse('download_document_pdf', kwargs={'token': token})
        url_completa = request.build_absolute_uri(url_relativa)
        
        # 3. Construimos el HTML
        # Opcional: Puedes agregar record.nombre o similar para que se vea mejor
        mensaje_html = f"""
            <html>
            <head></head>
            <body>
                <p>{cuerpo}</p>
                <br>
                <p>
                    Puede descargar el documento <b>{record.document_pdf.name}</b> en el siguiente enlace:
                </p>
                <p>
                    <a href="{url_completa}" style="padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">
                        Descargar Documento
                    </a>
                </p>
                <p><small>Este enlace es temporal.</small></p>
            </body>
            </html>
        """

        # 4. Enviamos el correo usando la función actualizada
        try:
            recipients = sendEmailWithCc(asunto, mensaje_html, main_email, cc_emails)
            return JsonResponse({
                "message": "Correo enviado correctamente", 
                "main_email": main_email,
                "cc_emails": cc_emails,
                "document_id": document_id
            })
        except Exception as e:
            return JsonResponse({"error": f"Error al enviar correo: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)
    
def downloadPdf(request, token):
    try:
        signer = TimestampSigner()
        doc_id = signer.unsign(token, max_age=int(settings.LINK_EXPIRATION))  # 7 días en segundos
        documento = get_object_or_404(Document, pk=doc_id)
        file_name = os.path.basename(documento.document_pdf.path)
        # Abre el archivo en modo binario
        file = open(documento.document_pdf.path, 'rb')
        
        # Crea la respuesta con el archivo
        response = FileResponse(file)
        
        # Configura los headers para forzar la descarga
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response['Content-Type'] = 'application/octet-stream'
        
        return response
    except SignatureExpired:
        context = {
            "title": "¡Enlace expirado!",
            "body": "El enlace que has utilizado para acceder al documento ha expirado. Por motivos de seguridad, los enlaces de descarga tienen un tiempo limitado de validez."
        }
        return render(request, 'gestor/invalid_link.html', context)
        #return HttpResponse("Este enlace ha expirado", status=410)
    except BadSignature:
        return HttpResponse("Enlace inválido", status=404)
    except:
        context = {
            "title": "¡Algo salió mal!",
            "body": "El enlace que has utilizado para acceder al documento no ha funcionado."
        }
        return render(request, 'gestor/invalid_link.html', context)


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
    return msg['To']

def sendEmailWithCc(subject, body, to_email, cc_emails_list=[]):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Si hay correos en copia, los agregamos al header 'Cc'
    if cc_emails_list:
        msg['Cc'] = ", ".join(cc_emails_list)

    msg.attach(MIMEText(body, 'html'))

    # Conectar con el servidor SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    # IMPORTANTE: En sendmail se deben poner TODOS los destinatarios (To + Cc)
    # para que el servidor sepa a quién entregar el mensaje.
    recipients = [to_email] + cc_emails_list
    
    server.sendmail(settings.EMAIL_HOST_USER, recipients, msg.as_string())

    server.quit()
    return recipients
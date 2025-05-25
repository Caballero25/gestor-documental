import io
import base64
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Document
from pyhanko.sign import signers, fields
from pyhanko.sign.fields import SigFieldSpec
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko import stamp
from pyhanko.pdf_utils.text import TextBoxStyle
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from gestor_documental.settings import MEDIA_ROOT
import time

@login_required
def signDocument(request, pk):
    document = get_object_or_404(Document, id=pk)
    protocolo = 'https' if request.is_secure() else 'http'
    dominio = request.get_host()
    url_base = f"{protocolo}://{dominio}"

    if not request.user.certificate:
        return JsonResponse({'message': 'No tienes un certificado digital configurado'}, status=400)

    if request.method == 'POST':
        try:
            pdfX, pdfY = document.get_pdf_size()
        except:
            pdfY = None
        try:
            # Parámetros del POST
            pagina = int(request.POST.get('pagina', 1)) - 1
            coordenadaX = float(request.POST.get('coordenadaX', 100))

            if pdfY:
                coordenadaY = (float(pdfY)-float(request.POST.get('coordenadaY', 100)))
            password = request.POST.get('password', '').encode('utf-8')

            # Leer certificado del usuario
            with request.user.certificate.open('rb') as cert_file:
                p12_bytes = cert_file.read()

            private_key, cert, additional_certs = pkcs12.load_key_and_certificates(
                p12_bytes, password, default_backend()
            )

            if not private_key:
                return JsonResponse({'message': 'Contraseña incorrecta o certificado inválido'}, status=400)

            signer = signers.SimpleSigner.load_pkcs12(
                pfx_file=MEDIA_ROOT + str(request.user.certificate),
                passphrase=password
            )

            # SOLUCIÓN: Solo normalizar si es la primera firma
            with document.file.open('rb') as original_pdf:
                pdf_data = original_pdf.read()
                
                # Verificar si el PDF ya tiene firmas
                reader = PdfReader(io.BytesIO(pdf_data))
                already_signed = False
                # Verifica si el documento tiene un formulario AcroForm
                acro_form_ref = reader.trailer["/Root"].get("/AcroForm")
                if acro_form_ref:
                    acro_form = acro_form_ref.get_object()  # <--- CORRECTO AQUÍ
                    fields_pdf = acro_form.get("/Fields", [])
                    for field in fields_pdf:
                        field_obj = field.get_object()
                        if field_obj.get("/FT") == "/Sig":
                            already_signed = True
                            break
                
                if not already_signed:
                    # Normalizar solo si no tiene firmas previas
                    normalized_pdf_io = io.BytesIO()
                    writer = PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)
                    writer.write(normalized_pdf_io)
                    normalized_pdf_io.seek(0)
                    w = IncrementalPdfFileWriter(normalized_pdf_io)
                else:
                    # Usar el PDF tal cual si ya tiene firmas
                    w = IncrementalPdfFileWriter(io.BytesIO(pdf_data))

            # Nombre único para el campo de firma
            field_name = f"FIRMA_{request.user.id}_{document.id}_{int(time.time())}"

            # Añadir campo de firma
            fields.append_signature_field(
                w,
                sig_field_spec=SigFieldSpec(
                    field_name,
                    box=(coordenadaX, coordenadaY, coordenadaX + 200, coordenadaY + 50),
                    on_page=pagina
                )
            )

            meta = signers.PdfSignatureMetadata(
                field_name=field_name,
                # Asegurar compatibilidad con firmas previas
                md_algorithm='sha256',
                subfilter=fields.SigSeedSubFilter.PADES
            )

            text_box_style = TextBoxStyle(
                font_size=18,
            )
            dataSignatory = {}
            for attribute in cert.subject:
                print(str(attribute.oid._name) + " exitoso")
                dataSignatory[attribute.oid._name] = attribute.value
            try:
                cn = dataSignatory['commonName']
                nombre_dividido = cn.split()
                nombres = " ".join(nombre_dividido[:2])
                apellidos = " ".join(nombre_dividido[2:])
                cn = f"{nombres}\n{apellidos}"
            except:
                print("No se pueden dividir los nombres")
            sample_text = f'Firmado electrónicamente\npor:\n{cn if cn else "%(signer)s"}\n'
            

            pdf_signer = signers.PdfSigner(
                meta,
                signer=signer,
                stamp_style=stamp.QRStampStyle(
                    stamp_text= sample_text + 'Validar únicamente\ncon FirmaEC',
                    text_box_style=text_box_style,
                    border_width=0
                ),
                # Permitir firmas incrementales
                new_field_spec=SigFieldSpec(
                    field_name,
                    box=(coordenadaX, coordenadaY, coordenadaX + 200, coordenadaY + 50),
                    on_page=pagina
                )
            )

            out = pdf_signer.sign_pdf(
                w,
                appearance_text_params={'url': url_base},
                existing_fields_only=False
            )

            # Guardar el PDF firmado correctamente
            file_name = document.file.name.split('/')[-1]
            document.file.delete()
            document.file.save(file_name, ContentFile(out.getvalue()), save=True)

            subject = cert.subject
            dataSignatory = {attr.oid._name: attr.value for attr in subject}

            return JsonResponse({
                'success': True,
                'message': 'Documento firmado con éxito!',
                'signer_info': dataSignatory
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al firmar el documento: {str(e)}'
            }, status=400)

    else:
        context = {
            'document': document,
            'file_base64': base64.b64encode(document.file.read()).decode('utf-8'),
            'mime_type': 'application/pdf'
        }
        return render(request, 'gestor/sign_document.html', context)
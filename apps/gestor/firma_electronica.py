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
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from gestor_documental.settings import MEDIA_ROOT
from pyhanko import stamp


@login_required
def signDocument(request, pk):
    document = get_object_or_404(Document, id=pk)

    if not request.user.certificate:
        return JsonResponse({'message': 'No tienes un certificado digital configurado'}, status=400)

    if request.method == 'POST':
        try:
            # Parámetros del POST
            pagina = int(request.POST.get('pagina', 1)) - 1
            coordenadaX = float(request.POST.get('coordenadaX', 100))
            coordenadaY = float(request.POST.get('coordenadaY', 100))
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

            # Normalizar el PDF (quitar hybrid xref)
            normalized_pdf_io = io.BytesIO()
            with document.file.open('rb') as original_pdf:
                reader = PdfReader(original_pdf)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                writer.write(normalized_pdf_io)

            normalized_pdf_io.seek(0)

            # Crear escritor incremental
            w = IncrementalPdfFileWriter(normalized_pdf_io)

            # Añadir campo de firma
            fields.append_signature_field(
                w,
                sig_field_spec=SigFieldSpec(
                    f"FIRMA_{request.user.id}_{document.id}",
                    box=(coordenadaX, coordenadaY, coordenadaX + 200, coordenadaY + 50),
                    on_page=pagina
                )
            )

            meta = signers.PdfSignatureMetadata(
                field_name=f"FIRMA_{request.user.id}_{document.id}"
            )

            pdf_signer = signers.PdfSigner(
                meta,
                signer=signer,
                stamp_style=stamp.QRStampStyle(
                    stamp_text='Firmado por: %(signer)s\nFecha: %(ts)s\n',
                )
                # No necesitamos allow_hybrid_xref=True porque ya está normalizado
            )

            out = pdf_signer.sign_pdf(
                w,
                appearance_text_params={'url': 'https://tudominio.com'}
            )

            # Guardar el PDF firmado sobre el archivo original
            file_path = document.file.name
            default_storage.delete(file_path)  # Elimina el archivo existente
            default_storage.save(file_path, ContentFile(out.getvalue()))  # Guarda el nuevo
            document.file = file_path  # Actualiza la referencia en el modelo
            document.save()

            subject = cert.subject
            dataSignatory = {attr.oid._name: attr.value for attr in subject}

            return JsonResponse({
                'message': 'Documento firmado con éxito!',
                'signer_info': dataSignatory
            })

        except Exception as e:
            return JsonResponse({
                'message': f'Error al firmar el documento: {str(e)}'
            }, status=400)

    else:
        context = {
            'document': document,
            'file_base64': base64.b64encode(document.file.read()).decode('utf-8'),
            'mime_type': 'application/pdf'
        }
        return render(request, 'gestor/sign_document.html', context)

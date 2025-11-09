from datetime import datetime
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers
from pyhanko import stamp
import os

### CAMBIAR
def signDoc(doc_path, password, path_certificate):
    try:
        password = password.encode('utf-8')
        signer = signers.SimpleSigner.load_pkcs12(
            pfx_file=path_certificate, passphrase=password
        )
    except Exception as e:
        print(f"Error al cargar credenciales: {e}")
        # Esta excepción será capturada y mostrada al usuario
        raise ValueError("Credenciales de firma inválidas. Verifique su contraseña.")

    if signer:
        try:
            with open(doc_path, 'rb') as doc:
                w = IncrementalPdfFileWriter(doc)
                total_pages = len(w.root['/Pages'].get_object()['/Kids'])

                fields.append_signature_field(
                    w, sig_field_spec=fields.SigFieldSpec(
                        'Signature',
                        box=(200, 50, 410, 100),
                        on_page=total_pages - 1
                    )
                )
                meta = signers.PdfSignatureMetadata(
                    field_name='Signature',
                    reason='Certificación oficial',
                    location='Tena, Ecuador'
                )
                pdf_signer = signers.PdfSigner(
                    meta,
                    signer=signer,
                    stamp_style=stamp.QRStampStyle(
                        stamp_text=f'Firmado electrónicamente por:\n{signer.subject_name}\nFecha: %(ts)s\n',
                    ),
                )
                
                firmante = f"FIRMADO POR: {signer.subject_name} FECHA: {datetime.now()}\nVALIDAR UNICAMENTE CON FirmaEC"
                
                out = pdf_signer.sign_pdf(
                    w, appearance_text_params={'url': firmante},
                )
                
                base_name, ext = os.path.splitext(doc_path)
                signed_doc_name = f"{base_name}-signed{ext}"
                
                with open(signed_doc_name, 'wb') as signed_pdf:
                    signed_pdf.write(out.getvalue())
                
                # --- !! ESTA ES LA CORRECCIÓN !! ---
                # Debe devolver la RUTA del archivo firmado, no 'True'
                return signed_doc_name 
                # --- !! FIN DE LA CORRECCIÓN !! ---
        
        except Exception as e:
            print(f"Error en el proceso de firma: {e}")
            raise Exception(f"Error interno durante la firma: {e}")
    else:
        raise ValueError("No se pudo inicializar el firmante, posiblemente las credenciales sean erroneas.")
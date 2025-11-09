from django.contrib.staticfiles import finders
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from .models import Document, TextoParametrizable
from .firma import signDoc  # Importa tu función de firma
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image
from datetime import datetime
import tempfile
import os
import io
import json

class DynamicPDFGenerator:
    def __init__(self, document, template_config=None):
        self.document = document
        self.template_config = template_config or {}
        self.buffer = io.BytesIO()
        
        # Registrar fuentes estándar
        self._register_fonts()
        #Tamanio del documento
        self.canvas_width = 800  # Ancho del canvas de Fabric.js
        self.canvas_height = 1000 # Alto del canvas de Fabric.js
        
        page_size_default = A4
        self.pdf_width = self.template_config.get('page_size', page_size_default)[0]
        self.pdf_height = self.template_config.get('page_size', page_size_default)[1]
        
        self.scale_x = self.pdf_width / self.canvas_width
        self.scale_y = self.pdf_height / self.canvas_height
    
    def _register_fonts(self):
        """Registrar fuentes disponibles"""
        # Fuentes estándar de ReportLab que ya están disponibles
        self.available_fonts = {
            'Helvetica': 'Helvetica',
            'Helvetica-Bold': 'Helvetica-Bold',
            'Helvetica-Oblique': 'Helvetica-Oblique',
            'Helvetica-BoldOblique': 'Helvetica-BoldOblique',
            'Times-Roman': 'Times-Roman',
            'Times-Bold': 'Times-Bold',
            'Times-Italic': 'Times-Italic',
            'Times-BoldItalic': 'Times-BoldItalic',
            'Courier': 'Courier',
            'Courier-Bold': 'Courier-Bold',
            'Courier-Oblique': 'Courier-Oblique',
            'Courier-BoldOblique': 'Courier-BoldOblique',
        }
        
        # Mapeo de fuentes comunes a fuentes de ReportLab
        self.font_mapping = {
            'Arial': 'Helvetica',
            'Times New Roman': 'Times-Roman',
            'Courier New': 'Courier',
            'Verdana': 'Helvetica',  # Similar a Helvetica
            'Georgia': 'Times-Roman',  # Similar a Times
        }
    
    def _get_reportlab_font(self, font_name):
        """Obtiene el nombre de fuente compatible con ReportLab"""
        if font_name in self.available_fonts:
            return font_name
        elif font_name in self.font_mapping:
            return self.font_mapping[font_name]
        else:
            # Por defecto usar Helvetica
            return 'Helvetica'
    
    def generate_pdf(self):
        """Genera el PDF dinámico basado en la configuración"""
        try:
            page_size = (self.pdf_width, self.pdf_height)
            self.c = canvas.Canvas(self.buffer, pagesize=page_size)
            pdf_title = f"acta_{self.document.metadata_schema.name}" or f"acta_{self.document.id}"
            self.c.setTitle(pdf_title)
            background_path = finders.find('img/bg_pdf.png')
            if not background_path:
                print("ADVERTENCIA: No se encontró la imagen de fondo en 'static/img/bg_pdf.png'")
            
            # Procesar páginas
            pages_config = self.template_config.get('pages', [])
            
            for page_num, page_config in enumerate(pages_config, 1):
                if page_num > 1:
                    self.c.showPage()
                if background_path:
                    self.c.drawImage(
                        background_path,
                        x=0, 
                        y=0,
                        width=self.pdf_width,
                        height=self.pdf_height,
                        preserveAspectRatio=False, 
                        mask='auto'
                    )
                
                # Agregar fondo si existe
                self._add_background(page_config)
                
                # Procesar elementos de la página
                elements = page_config.get('elements', [])
                for element in elements:
                    self._add_element(element)
            
            self.c.save()
            self.buffer.seek(0)
            return self.buffer
            
        except Exception as e:
            print(f"Error en generate_pdf: {e}")
            raise
            
        except Exception as e:
            print(f"Error en generate_pdf: {e}")
            raise
    
    def _add_background(self, page_config):
        """Agrega fondo a la página si está configurado"""
        # Implementar si necesitas fondos
        pass
    
    def _add_element(self, element):
        """Agrega un elemento al PDF"""
        try:
            element_type = element.get('type')
            
            if element_type == 'image':
                self._add_image_element(element)
            elif element_type == 'text':
                self._add_text_element(element) 
            elif element_type == 'dynamic_text':
                self._add_dynamic_text_element(element)
                
        except Exception as e:
            print(f"Error al agregar elemento {element_type}: {e}")
    def _add_image_element(self, element):
        """Agrega una imagen al PDF"""
        try:
            image_field = element.get('image_field', 'file')
            image_file = getattr(self.document, image_field, None)
            
            if not image_file:
                print(f"Archivo de imagen no encontrado: {image_field}")
                return
                
            # --- MODIFICADO: Aplicar escalas (como antes) ---
            x = element.get('x', 0) * self.scale_x
            y_fabric = element.get('y', 0) * self.scale_y
            width = element.get('width', 100) * self.scale_x
            height = element.get('height', 100) * self.scale_y
            rotation = element.get('rotation', 0)
            
            y = self.pdf_height - y_fabric - height
            
            with image_file.open('rb') as f:
                
                temp_file_path = None # Definir la variable fuera del with
                
                # --- INICIO DE CORRECCIÓN: Manejo de archivo temporal ---
                # Crear archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_file.write(f.read())
                    temp_file.flush()
                    # Guardamos la ruta
                    temp_file_path = temp_file.name
                    # Cerramos el archivo para que PIL pueda acceder a él
                    temp_file.close()
                # --- FIN DE CORRECCIÓN ---
                    
                if temp_file_path: # Asegurarse de que la ruta se obtuvo
                    try:
                        # Usar PIL para procesar la imagen desde la ruta (el archivo ya está cerrado)
                        pil_image = Image.open(temp_file_path)
                        
                        # Rotar si es necesario
                        if rotation:
                            pil_image = pil_image.rotate(-rotation, expand=True, resample=Image.BICUBIC)
                        
                        # Convertir a RGB (esta sigue siendo una buena práctica)
                        if pil_image.mode != 'RGB':
                            pil_image = pil_image.convert('RGB')
                        
                        # Guardar imagen procesada
                        img_buffer = io.BytesIO()
                        pil_image.save(img_buffer, format='JPEG', quality=85)
                        img_buffer.seek(0)
                        
                        # Dibujar imagen en el PDF
                        self.c.drawImage(ImageReader(img_buffer), x, y, width, height)
                        
                    except Exception as img_error:
                        print(f"Error procesando imagen: {img_error}")
                        # Intentar cargar la imagen directamente
                        self.c.drawImage(temp_file_path, x, y, width, height)
                    
                    finally:
                        # Limpiar archivo temporal
                        os.unlink(temp_file_path)
            
        except Exception as e:
            # Este es el log que viste
            print(f"Error crítico al agregar imagen: {e}")
    def _add_text_element(self, element):
        """Agrega texto estático al PDF"""
        try:
            lines = element.get('lines', [])

            x = element.get('x', 0) * self.scale_x
            y_fabric = element.get('y', 0) * self.scale_y
            font_size = element.get('font_size', 12) * self.scale_y
            font_family_input = element.get('font_family', 'Times New Roman')
            

            y = self.pdf_height - y_fabric - font_size
            
            font_family = self._get_reportlab_font(font_family_input)
            self.c.setFont(font_family, font_size)

            leading = font_size * 1.2 

            for i, line in enumerate(lines):
                line_y = y - (i * leading)
                if line_y < 0:  # Si se sale de la página
                    break
                self.c.drawString(x, line_y, line)
            
        except Exception as e:
            print(f"Error agregando texto: {e}")
    
    def _add_dynamic_text_element(self, element):
        """Agrega texto dinámico al PDF"""
        try:
            lines = element.get('lines', [])

            x = element.get('x', 0) * self.scale_x
            y_fabric = element.get('y', 0) * self.scale_y
            font_size = element.get('font_size', 12) * self.scale_y
            font_family_input = element.get('font_family', 'Times New Roman')
            
            # Ajustar coordenada Y
            y = self.pdf_height - y_fabric - font_size
            
            # Interlineado proporcional
            leading = font_size * 1.2 
            
            # Obtener fuente compatible
            font_family = self._get_reportlab_font(font_family_input)
            
            self.c.setFont(font_family, font_size)

            for i, line in enumerate(lines):
                line_y = y - (i * leading)
                if line_y < 0: 
                    break
                self.c.drawString(x, line_y, line)
                
        except Exception as e:
            print(f"Error agregando texto dinámico: {e}")


class PDFBuilderView(TemplateView):
    template_name = 'metadata/pdf_parametrizable/crud.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document_id = self.kwargs.get('document_id')
        document = get_object_or_404(Document, id=document_id)
        context['document'] = Document.objects.get(id=document_id)
        plantilla_json = None
        if document.metadata_schema:
            try:
                texto_para = TextoParametrizable.objects.get(schema=document.metadata_schema)
                if texto_para.plantilla_pdf:
                    plantilla_json = json.dumps(texto_para.plantilla_pdf)
            except TextoParametrizable.DoesNotExist:
                pass
        
        context['plantilla_json'] = plantilla_json
        return context


class GeneratePDFView(View):
    def post(self, request, document_id):
        
        # Rutas para archivos temporales que debemos limpiar
        temp_unsigned_path = None
        temp_signed_path = None

        try:
            print("=== INICIANDO GENERACIÓN PDF ===")
            document = get_object_or_404(Document, id=document_id)
            
            data = json.loads(request.body)
            template_config = data.get('template_config')
            cert_password = data.get('certificate_password')
            
            print(f"Documento: {document}")
            print(f"¿Solicita firma?: {'Sí' if cert_password else 'No'}")
            
            generator = DynamicPDFGenerator(document, template_config)
            pdf_buffer = generator.generate_pdf()
            pdf_buffer.seek(0)
            
            # 1. Eliminar el PDF físico anterior, si existe
            if document.document_pdf:
                print(f"Eliminando PDF anterior: {document.document_pdf.name}")
                if os.path.isfile(document.document_pdf.path):
                    os.remove(document.document_pdf.path)
                document.document_pdf.delete(save=False) # Borrar referencia del modelo

            # 2. Definir el nombre de archivo ESTÁTICO
            pdf_filename = f"doc_{document.id}_parametrizable.pdf"
            
            # 3. Lógica de Firma y Guardado
            if cert_password:
                # --- QUIERE FIRMAR ---
                print("Iniciando proceso de firma...")
                
                if not request.user.certificate or not request.user.certificate.path:
                    raise ValueError('No tiene un certificado digital cargado en su perfil.')
                
                cert_path = request.user.certificate.path
                if not os.path.exists(cert_path):
                    raise ValueError(f'Archivo de certificado no encontrado en la ruta: {cert_path}')
                
                # 3.1. Guardar el PDF (sin firmar) en un ARCHIVO TEMPORAL
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_f:
                    temp_f.write(pdf_buffer.read())
                    temp_unsigned_path = temp_f.name # Guardar ruta para firmar y limpiar
                print(f"PDF (temporal sin firmar) guardado en: {temp_unsigned_path}")
                
                # 3.2. Llamar a la función de firma
                temp_signed_path = signDoc(temp_unsigned_path, cert_password, cert_path)
                print(f"PDF (temporal firmado) generado en: {temp_signed_path}")
                
                # 3.3. Leer el PDF firmado para guardarlo
                with open(temp_signed_path, 'rb') as f_signed:
                    final_content = f_signed.read()
                
                print("PDF firmado leído.")

            else:
                # --- NO QUIERE FIRMAR ---
                print("Guardando PDF sin firmar...")
                final_content = pdf_buffer.read() # Obtener contenido del buffer

            # 4. GUARDAR EN EL MODELO (UNA SOLA VEZ)
            # Ya sea firmado o no, 'final_content' tiene el PDF correcto
            document.document_pdf.save(pdf_filename, ContentFile(final_content), save=True)
            print(f"PDF guardado exitosamente en: {document.document_pdf.path}")

            # 5. Enviar el PDF (firmado o no) de vuelta al frontend
            pdf_buffer = io.BytesIO(final_content) # Usar el contenido final
            pdf_buffer.seek(0)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="documento_generado.pdf"'
            
            print("=== PDF GENERADO Y GUARDADO EXITOSAMENTE ===")
            return response
            
        except (Document.DoesNotExist, ValueError) as e:
            error_msg = str(e)
            print(f"Error de negocio: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)
            
        except json.JSONDecodeError as e:
            error_msg = f"Error decodificando JSON: {str(e)}"
            print(error_msg)
            return JsonResponse({'error': error_msg}, status=400)
            
        except Exception as e:
            error_msg = f"Error inesperado generando PDF: {str(e)}"
            print(error_msg)
            return JsonResponse({'error': error_msg}, status=400)

        finally:
            # Limpieza de TODOS los archivos temporales
            if temp_signed_path and os.path.isfile(temp_signed_path):
                os.remove(temp_signed_path)
                print(f"Archivo temporal de firma eliminado: {temp_signed_path}")
            if temp_unsigned_path and os.path.isfile(temp_unsigned_path):
                os.remove(temp_unsigned_path)
                print(f"Archivo temporal sin firmar eliminado: {temp_unsigned_path}")

class SaveTemplateView(View):
    def post(self, request, document_id):
        try:
            # 1. Obtener el documento y su esquema
            document = get_object_or_404(Document, id=document_id)
            if not document.metadata_schema:
                return JsonResponse({'error': 'El documento no tiene un esquema de metadatos.'}, status=400)
            
            texto_para, created = TextoParametrizable.objects.get_or_create(
                schema=document.metadata_schema,
                defaults={'plantilla_texto': ''} # Añade un default si se crea
            )
            
            # 3. Parsear y guardar la plantilla
            template_config = json.loads(request.body)
            texto_para.plantilla_pdf = template_config
            texto_para.save()
            
            return JsonResponse({'success': True, 'message': 'Plantilla guardada exitosamente.'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
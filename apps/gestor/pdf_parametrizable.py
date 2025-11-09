# services/pdf_generator.py
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import fonts
from PIL import Image
import tempfile
import os

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
            
            # Procesar páginas
            pages_config = self.template_config.get('pages', [])
            
            for page_num, page_config in enumerate(pages_config, 1):
                if page_num > 1:
                    self.c.showPage()
                
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
        
import json
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import TemplateView
from .models import Document

class PDFBuilderView(TemplateView):
    template_name = 'metadata/pdf_parametrizable/crud.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document_id = self.kwargs.get('document_id')
        context['document'] = Document.objects.get(id=document_id)
        return context

class GeneratePDFView(View):
    def post(self, request, document_id):
        try:
            print("=== INICIANDO GENERACIÓN PDF ===")
            document = Document.objects.get(id=document_id)
            print(f"Documento: {document}")
            
            # Log del body recibido
            body_str = request.body.decode('utf-8')
            print(f"Body recibido: {body_str[:500]}...")  # Primeros 500 chars
            
            template_config = json.loads(request.body)
            print(f"Configuración parseada: {json.dumps(template_config, indent=2)[:500]}...")
            
            generator = DynamicPDFGenerator(document, template_config)
            pdf_buffer = generator.generate_pdf()
            
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="documento_generado.pdf"'
            
            print("=== PDF GENERADO EXITOSAMENTE ===")
            return response
            
        except Document.DoesNotExist:
            error_msg = f"Documento con id {document_id} no existe"
            print(error_msg)
            return JsonResponse({'error': error_msg}, status=404)
            
        except json.JSONDecodeError as e:
            error_msg = f"Error decodificando JSON: {str(e)}"
            print(error_msg)
            return JsonResponse({'error': error_msg}, status=400)
            
        except Exception as e:
            error_msg = f"Error generando PDF: {str(e)}"
            print(error_msg)
            return JsonResponse({'error': error_msg}, status=400)

class SaveTemplateView(View):
    def post(self, request, document_id):
        try:
            data = json.loads(request.body)
            template_config = data.get('template_config')
            
            # Aquí podrías guardar la plantilla en la base de datos
            # para uso futuro
            
            return JsonResponse({'success': True, 'message': 'Plantilla guardada'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
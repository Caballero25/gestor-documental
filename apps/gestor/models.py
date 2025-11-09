from django.db import models
from ..metadata.models import MetadataSchema
from PyPDF2 import PdfReader
import re

# Create your models here.
class TextoParametrizable(models.Model):
    """
    Guarda la plantilla de texto que se usará para documentos ligados 
    a un MetadataSchema específico.
    """
    schema = models.OneToOneField(
        MetadataSchema, 
        on_delete=models.CASCADE, 
        verbose_name='Esquema de Metadatos'
    )
    plantilla_texto = models.TextField(
        verbose_name='Plantilla de Texto'
    )

    plantilla_pdf = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name="Plantilla PDF Parametrizable"
    )
    
    class Meta:
        verbose_name = "Texto Parametrizable"
        verbose_name_plural = "Textos Parametrizables"
        
    def __str__(self):
        return f"Plantilla para {self.schema.name}"


class Document(models.Model):
    code_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre - identificador')
    file = models.FileField(upload_to="documents/", verbose_name='Documento')
    file2 = models.FileField(upload_to="documents/", verbose_name='Documento 2', null=True, blank=True)
    metadata_schema = models.ForeignKey(MetadataSchema, blank=True, null=True,on_delete=models.PROTECT, verbose_name='Esquema de Metadatos')
    metadata_values = models.JSONField(default=dict, blank=True, null=True)  # Aquí se guardan los valores de los metadatos
    indexado = models.BooleanField(default=False, blank=True, null=True) 

    def __str__(self):
        return f"Documento: {self.file}"
    def get_pdf_size(self, unit="pt"):
        """
        Obtiene el tamaño (ancho, alto) del PDF en puntos (pt) o milímetros (mm).
        
        Args:
            unit (str): "pt" (puntos) o "mm" (milímetros).
        
        Returns:
            tuple: (ancho, alto) en la unidad especificada.
        
        Raises:
            ValueError: Si el archivo no es un PDF válido.
        """
        if not self.file:
            return None
        
        try:
            # Abrir el archivo PDF
            with self.file.open(mode='rb') as pdf_file:
                reader = PdfReader(pdf_file)
                if not reader.pages:
                    return None
                
                # Obtener la primera página
                page = reader.pages[0]
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
                
                if unit == "mm":
                    # Convertir puntos (pt) a milímetros (mm)
                    width /= 2.83465
                    height /= 2.83465
                
                return round(width, 2), round(height, 2)
        
        except Exception as e:
            raise ValueError(f"No se pudo leer el PDF: {e}")
    def generar_texto_final(self):
        """
        Genera el texto final sustituyendo las claves de la plantilla
        con los valores reales de metadata_values.
        """
        if not self.metadata_schema:
            return "Error: Documento sin esquema de metadatos asociado."
            
        try:
            # 1. Obtener la plantilla de texto para el esquema
            texto_parametrizable = TextoParametrizable.objects.get(schema=self.metadata_schema)
            plantilla = texto_parametrizable.plantilla_texto
        except TextoParametrizable.DoesNotExist:
            return f"Advertencia: No existe una plantilla de texto para el esquema '{self.metadata_schema.name}'."

        # 2. Definir la función de reemplazo
        # El patrón busca cualquier texto que esté entre corchetes, ej: [CLAVE]
        # El grupo de captura (1) será el texto dentro de los corchetes (la clave del metadato)
        patron_sustitucion = r"\[([^\]]+)\]"
        
        # Función que se ejecutará por cada coincidencia encontrada por re.sub
        def sustituir_clave(match):
            clave = match.group(1) # Obtiene la clave, ej: 'BAUTIZADO'
            
            # Buscar el valor en el diccionario de metadatos
            valor = self.metadata_values.get(clave)
            
            # Formatear el valor
            if valor is None:
                # Si el valor es null/None o no existe la clave, se reemplaza por una cadena vacía o un marcador
                return "" # O podrías usar f"[[CLAVE NO ENCONTRADA: {clave}]]" para depurar
            else:
                # Se convierte a string, asegurando que números o fechas se manejen
                return str(valor)

        # 3. Ejecutar la sustitución
        texto_final = re.sub(patron_sustitucion, sustituir_clave, plantilla)
        
        # 4. Retornar el resultado
        return texto_final
        
class DocumentSequence(models.Model):
    libro = models.CharField(max_length=200, verbose_name="Tipo de libro a digitalizar", default="BAUTIZO", null=False, blank=False)
    seq_value = models.BigIntegerField(default=1)

    def __str__(self):
        return f"Secuencia actual: {self.seq_value}"
    

### PDF'S PARAMETRIZABLES
class PDFTemplate(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nombre de plantilla')
    default_width = models.FloatField(default=595.27)  # A4 ancho en puntos
    default_height = models.FloatField(default=841.89)  # A4 alto en puntos
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class PDFElement(models.Model):
    ELEMENT_TYPES = [
        ('image', 'Imagen'),
        ('text', 'Texto'),
        ('dynamic_text', 'Texto Dinámico'),
    ]
    
    template = models.ForeignKey(PDFTemplate, on_delete=models.CASCADE, related_name='elements')
    element_type = models.CharField(max_length=20, choices=ELEMENT_TYPES)
    x_position = models.FloatField(verbose_name='Posición X (pt)')
    y_position = models.FloatField(verbose_name='Posición Y (pt)')
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    rotation = models.FloatField(default=0, verbose_name='Rotación (grados)')
    content = models.TextField(blank=True, null=True)  # Para texto estático
    page = models.IntegerField(default=1)
    font_size = models.IntegerField(default=12, null=True, blank=True)
    font_family = models.CharField(max_length=50, default='Helvetica', blank=True)
    
    class Meta:
        ordering = ['page', 'id']
    
    def __str__(self):
        return f"{self.element_type} - Página {self.page}"
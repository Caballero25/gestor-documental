from django.db import models
from ..metadata.models import MetadataSchema
from PyPDF2 import PdfReader

# Create your models here.
class Document(models.Model):
    code_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre - identificador')
    file = models.FileField(upload_to="documents/", verbose_name='Documento')
    metadata_schema = models.ForeignKey(MetadataSchema, blank=True, null=True,on_delete=models.PROTECT, verbose_name='Esquema de Metadatos')
    metadata_values = models.JSONField(default=dict, blank=True, null=True)  # Aquí se guardan los valores de los metadatos
    indexado = models.BooleanField(default=False, blank=True, null=True)  # Aquí se guardan los valores de los metadatos

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
        
class DocumentSequence(models.Model):
    libro = models.CharField(max_length=200, verbose_name="Tipo de libro a digitalizar", default="BAUTIZO", null=False, blank=False)
    seq_value = models.BigIntegerField(default=1)

    def __str__(self):
        return f"Secuencia actual: {self.seq_value}"
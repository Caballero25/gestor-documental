from django.db import models
from ..metadata.models import MetadataSchema

# Create your models here.
class Document(models.Model):
    code_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre - identificador')
    file = models.FileField(upload_to="documents/", verbose_name='Documento')
    metadata_schema = models.ForeignKey(MetadataSchema, blank=True, null=True,on_delete=models.PROTECT, verbose_name='Esquema de Metadatos')
    metadata_values = models.JSONField(default=dict, blank=True, null=True)  # Aquí se guardan los valores de los metadatos

    def __str__(self):
        return f"Documento: {self.file}"
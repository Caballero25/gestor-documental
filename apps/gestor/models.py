from django.db import models
from ..metadata.models import MetadataSchema

# Create your models here.
class Document(models.Model):
    code_name = models.CharField(max_length=200)
    file = models.FileField(upload_to="documents/")
    metadata_schema = models.ForeignKey(MetadataSchema, blank=True, null=True,on_delete=models.PROTECT)
    metadata_values = models.JSONField(default=dict, blank=True, null=True)  # Aquí se guardan los valores de los metadatos

    def __str__(self):
        return f"Documento de {self.file}"
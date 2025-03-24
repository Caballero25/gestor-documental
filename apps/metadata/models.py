from django.db import models

class MetadataField(models.Model):
    FIELD_TYPES = [
        ('text', 'Texto'),
        ('number', 'Número'),
        ('date', 'Fecha'),
        ('select', 'Selección'),
        ('checkbox', 'Casilla de verificación'),
    ]

    name = models.CharField(max_length=255, unique=True, blank=False, verbose_name="Nombre del campo")  # Label
    field_type = models.CharField(max_length=50, blank=False, choices=FIELD_TYPES, verbose_name="Tipo de dato")  # Data type
    options = models.JSONField(blank=True, null=True, verbose_name="Opciones del select separadas por una coma (,)")  # Select option (json)

    def __str__(self):
        return f"{self.name} ({self.get_field_type_display()})"
class MetadataSchema(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, verbose_name="Nombre del esquema") 
    fields = models.ManyToManyField(MetadataField, blank=False, related_name='schema_fields', verbose_name='Campos del esquema')
    def __str__(self):
        return self.name
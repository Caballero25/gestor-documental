from django.db import models

# Create your models here.

class Module(models.Model):
    name = models.CharField(max_length=20, unique=True, null=False, blank=False, verbose_name="Nombre del modulo")
    icon = models.CharField(max_length=20, unique=True, null=False, blank=False, verbose_name="Ícono del modulo")
    is_visible = models.BooleanField(default=True, verbose_name='Visible')

    def __str__(self):
        return self.name

class SubModule(models.Model):
    name = models.CharField(max_length=20, unique=True, null=False, blank=False, verbose_name="Nombre del modulo")
    url_name = models.CharField(max_length=100, verbose_name='URL', unique=True, blank=False)
    is_visible = models.BooleanField(default=True, verbose_name='Visible')
    module = models.ForeignKey(Module, null=False, blank=False, verbose_name='Menú',
                                   on_delete=models.PROTECT)
    
    def __str__(self):
        return self.name
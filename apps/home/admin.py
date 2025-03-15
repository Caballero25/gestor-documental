from django.contrib import admin

# Register your models here.
from .models import Module, SubModule

admin.site.register(Module)
admin.site.register(SubModule)
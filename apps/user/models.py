from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from .managers import UserManager
from django.urls import reverse
from django.conf import settings

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ("MASCULINO", "MASCULINO"),
        ("FEMENINO", "FEMENINO"),
        ("PREFIERO NO DECIRLO", "PREFIERO NO DECIRLO")
    )
    email = models.EmailField(unique=True, max_length=50, blank=False, verbose_name='Correo Electrónico')
    username = models.CharField(max_length=40, blank=False, null=False, verbose_name='Nombre de usuario')
    gender = models.CharField(null=True, default="PREFIERO NO DECIRLO", choices=GENDER_CHOICES, verbose_name='Género')
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True, default='avatars/no-gender.png')
    certificate = models.FileField(upload_to="certificados/", null=True, blank=True,
                                   verbose_name='certificado digital')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    groups = models.ManyToManyField(Group, verbose_name=('groups'), blank=True, related_name='user_groups')
    user_permissions = models.ManyToManyField(
        Permission, verbose_name=('user permissions'), blank=True, related_name='user_user_permissions'
    )
    USERNAME_FIELD ='email'
    is_staff = models.BooleanField(default=True)

    objects = UserManager()
    
    def __str__(self):
        return self.username
    
    class Meta:
        ordering = ['-created_at']    
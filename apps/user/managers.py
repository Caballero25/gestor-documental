from django.db import models
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager, models.Manager):
    def create_user(self, email, password, username, **extra_fields):
        user = self.model(
            email = email,
            username = username,
            is_staff = True,
            is_superuser = False,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user
    def create_superuser(self, email, password, username="ADMINISTRACIÓN", **extra_fields):
        u = self.create_user(email, password, username, **extra_fields)
        u.is_admin = True
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u
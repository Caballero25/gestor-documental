from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django import forms
from django.forms.widgets import ClearableFileInput
from .models import User

#   USERS
class CustomClearableFileInput(ClearableFileInput):
    clear_checkbox_label = "Eliminar certificado"
    initial_text = ""
    input_text = "Cambiar certificado"
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'gender', 'certificate', 'is_active', 'groups']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del usuario'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'gender': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
            }),
            'certificate': CustomClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'groups': forms.CheckboxSelectMultiple(attrs={'class': ''}),
        }
        error_messages = {
            'username': {
                'required': _("El nombre del usuario es obligatorio."),
            },
            'email': {
                'unique': _("Este correo electrónico ya está siendo utilizado por otro usuario."),
                'required': _("El correo electrónico es obligatorio."),
            },
        }
    def save(self, commit=True):
        user = super().save(commit=False)  # No guarda inmediatamente
        if user.gender == "MASCULINO":
            user.avatar = "avatars/male-color.png"
        elif user.gender == "FEMENINO":
            user.avatar = "avatars/female-color.png"
        else:
            user.avatar = "avatars/no-gender.png"
        if commit:
            user.save()
        return user
    

class CreateUserForm(UserForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        label="Contraseña"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        label="Confirmar Contraseña"
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")

        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False) 
        password1 = self.cleaned_data.get("password1")
        if user.gender == "MASCULINO":
            user.avatar = "avatars/male-color.png"
        elif user.gender == "FEMENINO":
            user.avatar = "avatars/female-color.png"
        else:
            user.avatar = "avatars/no-gender.png"
        user.set_password(password1)
        if commit:
            user.save()
        return user
    
#   GROUPS
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del grupo'}),
            'permissions': forms.CheckboxSelectMultiple(attrs={'class': ''}),
        }
        labels = {
            'permissions': 'Permisos que tendrá el grupo:',  # Aquí cambias el label de "Permissions" a "Permisos"
        }
        error_messages = {
            'name': {
                'unique': _("Ya existe un grupo con el nombre ingresado."),
                'required': _("El nombre del grupo es obligatorio."),
            },
        }
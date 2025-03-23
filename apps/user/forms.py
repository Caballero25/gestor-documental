from django.utils.translation import gettext_lazy as _
from django import forms
from django.forms.widgets import ClearableFileInput
from .models import User
class CustomClearableFileInput(ClearableFileInput):
    clear_checkbox_label = "Eliminar certificado"
    initial_text = ""
    input_text = "Cambiar certificado"
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'gender', 'certificate', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del usuario'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'gender': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
            }),
            'certificate': CustomClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
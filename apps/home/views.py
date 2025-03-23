from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from http import HTTPStatus
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic import ListView
from .models import Module
from .forms import ModuleForm

# Create your views here.
@login_required
def home(request):
    return render(request, "home/home.html")


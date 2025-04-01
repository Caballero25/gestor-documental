from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
    return render(request, "home/home.html")

def permission_denied(request, reason=""):
    return render(request, "403.html")
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


def dashboard_view(request):
    return render(request, "dashboard.html", {})

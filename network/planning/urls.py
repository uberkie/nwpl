from django.urls import path, include
from planning.views import dashboard_view, add_device

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('add_device/', add_device, name='add_device'),
]

from django.urls import path, include
from planning.views import dashboard_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
]

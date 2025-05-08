from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('datosPacientes/', views.alarm_list),
    path('createDatosPaciente/', views.generate_alarm),
]
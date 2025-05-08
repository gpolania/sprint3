

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import include

from . import views


urlpatterns = [
    path('pacientes/', views.paciente_list, name='pacienteList'),
    path('paciente/<int:id>', views.single_paciente, name='singlePaciente'),
    path('paciente/create/', views.paciente_create, name='pacienteCreate'),
    path('paciente/edit/<int:pk>/', views.paciente_edit, name='pacienteEdit'),

]
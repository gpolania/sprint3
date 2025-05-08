from .models import Paciente
from django import forms

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'edad', 'genero', 'fecha_ingreso', 'diagnostico']

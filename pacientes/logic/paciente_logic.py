from ..models import Paciente

def get_pacientes():
    return Paciente.objects.all()

def get_paciente(id):
    return Paciente.objects.get(pk=id)

def create_paciente(form):
    form.save()

def update_paciente(paciente, form):
    if form.is_valid():
        form.save()

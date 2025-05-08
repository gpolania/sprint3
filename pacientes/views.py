from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse


from .forms import PacienteForm
from .logic.paciente_logic import get_pacientes, get_paciente, create_paciente, update_paciente

from django.contrib.auth.decorators import login_required
from monitoring.auth0backend import getRole
from .models import Paciente 

@login_required
def paciente_list(request):
    pacientes = get_pacientes()
    return render(request, 'Paciente/pacientes.html', {'paciente_list': pacientes})

@login_required
def single_paciente(request, id=0):
    paciente = get_paciente(id)
    return render(request, 'Paciente/paciente.html', {'paciente': paciente})

@login_required
def paciente_create(request):
    role = getRole(request)
    if role == "Medico":
        if request.method == 'POST':
            form = PacienteForm(request.POST)
            if form.is_valid():
                create_paciente(form)
                messages.success(request, 'Paciente creado exitosamente')
                return HttpResponseRedirect(reverse('pacienteList'))
        else:
            form = PacienteForm()
        return render(request, 'Paciente/pacienteCreate.html', {'form': form})
    else:
        return HttpResponse("Unauthorized User")

@login_required
def paciente_edit(request, pk):
    role = getRole(request)
    
    if role != "Medico":
        return HttpResponse("Unauthorized User")
    
    paciente = get_object_or_404(Paciente, id=pk)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()  # Actualiza el paciente existente
            return HttpResponseRedirect(reverse('pacienteList'))
    else:
        form = PacienteForm(instance=paciente)
    
    return render(request, 'Paciente/pacienteEdit.html', {'form': form})
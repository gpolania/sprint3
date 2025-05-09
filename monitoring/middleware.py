from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Variable
from .forms import VariableForm
from monitoring.auth0backend import getRole
import re

def check_business_hours():
    """Verifica si está fuera del horario laboral (7am-5pm L-V)"""
    now = timezone.now()
    if now.weekday() >= 5:  # Fin de semana
        return True
    if now.hour < 7 or now.hour >= 17:  # Fuera de horario laboral
        return True
    return False

def detect_sql_injection(request):
    """Detecta patrones de SQL injection en la solicitud"""
    sql_patterns = [
        r';.*DROP', r';.*DELETE', r';.*UPDATE',
        r';.*INSERT', r'UNION.*SELECT', r'OR\s+1=1',
        r'--', r'/\*.*\*/'
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, request.path, re.IGNORECASE) or \
           re.search(pattern, request.META.get('QUERY_STRING', ''), re.IGNORECASE):
            return True
    return False

def send_alert(request):
    """Envía alerta por correo electrónico"""
    subject = 'ALERTA: Intento de SQL Injection Detectado'
    message = f'''
    Intento de ataque detectado:
    - Hora: {timezone.now()}
    - IP: {request.META.get('REMOTE_ADDR')}
    - Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}
    - Ruta: {request.path}
    '''
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        ['sebastianc290701@gmail.com'],
        fail_silently=False,
    )

def variable_list(request):
    if not check_business_hours() and detect_sql_injection(request):
        send_alert(request)
        return HttpResponseForbidden('Acceso no permitido fuera de horario laboral')
    
    role = getRole(request)
    if role not in ["Gerencia Campus", "Supervisor"]:
        return HttpResponseForbidden("No tiene permisos para acceder a esta sección")
    
    variables = Variable.objects.all()
    return render(request, 'Variable/variables.html', {'variables': variables})

def variable_detail(request, id):
    if not check_business_hours() and detect_sql_injection(request):
        send_alert(request)
        return HttpResponseForbidden('Acceso no permitido fuera de horario laboral')
    
    if not str(id).isdigit():
        return HttpResponseForbidden("ID inválido")
    
    variable = get_object_or_404(Variable, id=id)
    return render(request, 'Variable/variable.html', {'variable': variable})

def variable_create(request):
    if not check_business_hours() and detect_sql_injection(request):
        send_alert(request)
        return HttpResponseForbidden('Acceso no permitido fuera de horario laboral')
    
    role = getRole(request)
    if role != "Gerencia Campus":
        return HttpResponseForbidden("No tiene permisos para crear variables")
    
    if request.method == 'POST':
        form = VariableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('variable-list')
    else:
        form = VariableForm()
    
    return render(request, 'Variable/variableCreate.html', {'form': form})

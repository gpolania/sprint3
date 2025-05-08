
from ..models import Alarm

def get_alarms():
    queryset = Alarm.objects.all()
    return (queryset)


def create_alarm(id, nombre, sangre, alergias,):
    alarm = Alarm()
    alarm.idPaciente = id
    alarm.nombre = nombre
    alarm.tipoSangre = sangre
    alarm.alergias = alergias
    alarm.save()
    return alarm
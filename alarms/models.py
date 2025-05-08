from django.db import models

class Alarm(models.Model):

    idPaciente = models.FloatField(null=True, blank=True, default=None)
    nombre = models.CharField(max_length=255, null=True, blank=True, default=None)
    tipoSangre = models.CharField(max_length=50, null=True, blank=True, default=None)
    alergias = models.CharField(max_length=255, null=True, blank=True, default=None)


    def __str__(self):
        return '{"idPaciente": ' + str(self.idPaciente) + ', "nombre": "' + str(self.nombre) + '", "tipoSangre": "' + str(self.tipoSangre) + '", "alergias": "' + str(self.alergias) + '"}'
    
    def toJson(self):
        alarm = {
            'idPaciente': self.idPaciente,
            'nombre': self.nombre,
            'tipoSangre': self.tipoSangre,
            'alergias': self.alergias
        }
        return alarm
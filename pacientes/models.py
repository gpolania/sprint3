from django.db import models

class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    edad = models.PositiveIntegerField()
    genero = models.CharField(max_length=10)
    fecha_ingreso = models.DateField()
    diagnostico = models.TextField()

    def __str__(self):
        return self.nombre

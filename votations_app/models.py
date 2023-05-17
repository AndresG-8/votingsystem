from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date
from django.utils import timezone

class Votation(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votaciones_creadas")
    title = models.CharField(max_length=255)
    description = models.TextField()
    initial_date = models.DateTimeField()
    final_date = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='votations_voters')

    def __str__(self):
        return f'{self.pk} - {self.title}'
   
    @staticmethod
    def get_active_votations():
        now = timezone.now()
        return Votation.objects.filter(initial_date__lte=now, final_date__gte=now)

    @staticmethod
    def is_active_votation():
        today = date.today()
        return Votation.objects.filter(initial_date__lte=today, final_date__gte=today)
    
    def is_active(self):
        """
        Se verifica si la votacione esta activa al día y hora actual, de esta manera mostrarlas y habilitar botones
        """
        now = timezone.now()
        return self.initial_date <= now <= self.final_date


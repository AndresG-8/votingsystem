from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
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

    @classmethod
    def get_upcoming_votations(cls):
        """
        Obtiene las votaciones con un mes de antelación
        """
        now = timezone.now().date()
        one_month_later = now + timedelta(days=30)
        upcoming_votations = cls.objects.filter(initial_date__gte=now, initial_date__lt=one_month_later)
        return upcoming_votations

    @classmethod
    def get_past_votations(cls):
        """
        Obtiene las votaciones con un mes de antelación
        """
        now = timezone.now().date()
        one_month_ago = now + timedelta(days=30)
        upcoming_votations = cls.objects.filter(initial_date__gte=one_month_ago, initial_date__lt=now)
        return upcoming_votations
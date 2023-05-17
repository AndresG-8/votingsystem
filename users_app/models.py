from django.db import models

from django.contrib.auth.models import User

#Este modelo aplica solo a los candidatos
class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    program = models.CharField(max_length=100)
    candidate_group = models.IntegerField(default=0)
    profile_image = models.FileField(upload_to='profile_images', null=True, blank=True)
    has_voted = models.BooleanField(default=False)
    is_candidate = models.BooleanField(default=False)
    is_substitute = models.BooleanField(default=False)
    votes_received = models.IntegerField(default=0)
    propossals = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.user.username} es candidato: {self.is_candidate} - suplente: { self.is_substitute} - ha votado: {self.has_voted} - grupo - {self.candidate_group}.'

#este modelo aplica a TODOS los usuarios, no solo a los elegidos como candidatos
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_user = models.CharField(max_length=100, unique=True)
    private_key = models.CharField(max_length=500)
    public_key = models.CharField(max_length=500)
    active = models.BooleanField(default=True)
    first_login = models.DateTimeField(null=True, blank=True)
    vote = models.IntegerField(default=1) #si es 1 es que no se ha gastado su voto

    def __str__(self):
        return self.user.username

# class UserVotation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     votation = models.ForeignKey(Votation, on_delete=models.CASCADE)
    
# Dosya: users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    dogum_tarihi = models.DateField(null=True, blank=True)
    dogum_saati = models.TimeField(null=True, blank=True)
    dogum_yeri = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    gunes_burcu = models.CharField(max_length=50, blank=True)
    ay_burcu = models.CharField(max_length=50, blank=True)
    yukselen_burc = models.CharField(max_length=50, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return self.email
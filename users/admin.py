# users/admin.py

from django.contrib import admin
from .models import CustomUser

# CustomUser modelini admin paneline kaydediyoruz.
admin.site.register(CustomUser)
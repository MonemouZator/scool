from django.contrib import admin

# Register your models here.

from personnel.models import Historique
from .models import Administrateur
from personnel.models import Token

admin.site.register(Token)

admin.site.register(Administrateur)

admin.site.register(Historique)
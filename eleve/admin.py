from django.contrib import admin

# Register your models here.
from .models import Eleve
from eleve.models import FraisScolarite
admin.site.register(Eleve)
admin.site.register(FraisScolarite)
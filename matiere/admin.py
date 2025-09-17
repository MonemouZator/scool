from django.contrib import admin

# Register your models here.
from .models import Matiere
from matiere.models import   EnseignantMatiere

admin.site.register(Matiere)

admin.site.register(EnseignantMatiere)
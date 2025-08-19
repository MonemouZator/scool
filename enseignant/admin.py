from django.contrib import admin

# Register your models here.from django.contrib import admin
from .models import Enseignant
from enseignant.models import PaiementSalaire
from enseignant.models import Depense
admin.site.register(Enseignant)

admin.site.register(PaiementSalaire)

admin.site.register(Depense)
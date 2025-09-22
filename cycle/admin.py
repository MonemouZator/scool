from django.contrib import admin

# Register your models here.
from .models import Cycle,Etablissement

admin.site.register(Cycle)

admin.site.register(Etablissement)
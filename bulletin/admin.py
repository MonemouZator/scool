from django.contrib import admin
from .models import BulletinTrimestriel,BulletinAnnuel


@admin.register(BulletinTrimestriel)
class BulletinTrimestrielAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'trimestre', 'annee_scolaire')
    search_fields = ('eleve__nom', 'annee_scolaire__nom')
    list_filter = ('trimestre', 'annee_scolaire')


@admin.register(BulletinAnnuel)
class BulletinAnnuelAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'annee_scolaire')
    search_fields = ('eleve__nom', 'annee_scolaire__nom')
    list_filter = ('annee_scolaire',)

from django.contrib import admin

# Register your models here.
from .models import Note





class NoteModelAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'matiere', 'note_comp', 'note_cours','annee_scolaire', 'moyenne')      
admin.site.register(Note,NoteModelAdmin)



admin.site.site_title = "Ecole"
admin.site.site_header = "Ecole"
admin.site.index_title = "Ecole"
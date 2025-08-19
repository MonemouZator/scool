

from django.urls import path
from . import views

urlpatterns = [

    # autres modèles d'URL
    path('note/cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeur', views.note, name='note'),  # Assurez-vous que le nom correspond
    path('enseignant/notation/smljmlkmkmlkmlkjkhjhfhhhf', views.Liste_note_enseignant, name='note_enseignant'),  # Assurez-vous que le nom correspond
    #path('ajout-note/',views.ajout_note,name='ajout-note'),# Chemin d'ajout  des informations
    path('modifie-note/cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeur',views.modifier,name='modifi-note'),# Chemin de modification  des informations
    path('supprime/<pk>/cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeur',views.supprimer,name='supprimer-note'),
    path('attribuer/note', views.attribuer_notes, name='attribuer-notes'),
    path('attributtion/cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeur', views.attribuer_note_enseignant, name='attribuer_note_enseignant'),


]

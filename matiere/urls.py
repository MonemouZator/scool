
from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [

    # autres modèles d'URL
    path('matiere', views.matiere, name='matiere'),  # Assurez-vous que le nom correspond
    path('gggg/',views.ajout,name='ajout-matiere'),# Chemin d'ajout  des informations
    path('modif/',views.modifier,name='modifi-matiere'),# Chemin de modification  des informations
    path('sup/<pk>/',views.supprimer,name='supprimer-matiere'),
   






]

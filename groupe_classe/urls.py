
from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [

    # autres modèles d'URL
    path('group', views.groupe, name='groupe'),  # Assurez-vous que le nom correspond
    path('gggg/',views.ajout,name='ajout-groupe'),# Chemin d'ajout  des informations
    path('modif/',views.modifier,name='modifi-groupe'),# Chemin de modification  des informations
    path('sup/<pk>/',views.supprimer,name='supprimer-groupe'),
   






]


from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [

    # autres modèles d'URL
    path('annee/scolaire/', views.annee_scolaire, name='an'),  # Assurez-vous que le nom correspond
    path('ajout-annee/',views.ajout,name='ajout-annee'),# Chemin d'ajout  des informations
    path('annee/',views.modifier,name='modifi-annee'),# Chemin de modification  des informations
    path('supprime/<pk>/',views.supprimer,name='supprimer-annee'),
    # path('detail/',views.detail_enseignant,name='detail'),






]

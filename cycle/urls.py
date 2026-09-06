from django.urls import path
from . import views

urlpatterns = [

    # Page principale des cycles
    path(
        'cycle-cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeuruuygcwqzs/',
        views.cycle,
        name='cycle'
    ),

    # Ajout cycle
    path(
        'cs/cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeuruuygcwqzs/',
        views.ajout,
        name='ajout-cycle'
    ),

    # Modification cycle (POST uniquement)
    path(
        'cycle/modifier/',
        views.modifier,
        name='modifier-cycle'
    ),

    # Suppression cycle
    path(
        'supprime/cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeuruuygcwqzs/<int:pk>/',
        views.supprimer,
        name='supprimer-cycle'
    ),

    # Profil établissement
    path('profil/etablissement/', views.profil_ecole, name='ajout_ecole'),
    path('enregistre-profil/etablissement/', views.enregistrement, name='enregistrement'),
    path('aficharge-profil/etablissement/', views.afficharge_info_ecole, name='afficharge_info_ecole'),

   path(
    'etablissement/modification/<int:pk>/',
    views.modifier_info_ecole,
    name='modifier_info_ecole'
),
    path(
        'supprime/etablissement/<int:pk>/',
        views.supprimer_ecole,
        name='supprimer-ecole'
    ),
]

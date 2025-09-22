
from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [

    # autres modèles d'URL
    path('cycle-cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeuruuygcwqzs/', views.cycle, name='cycle'),  # Assurez-vous que le nom correspond
    path('cs/cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeuruuygcwqzs',views.ajout,name='ajout-cycle'),# Chemin d'ajout  des informations
    path('cycle/cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeuruuygcwqzs',views.modifier,name='modifi-cycle'),# Chemin de modification  des informations
    path('supprime/cklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeuruuygcwqzs<pk>/',views.supprimer,name='supprimer-cycle'),
    path('profil/etablissement', views.profil_ecole, name='ajout_ecole'), 
    path('enregistre-profil/etablissement', views.enregistrement, name='enregistrement'), 
    path('aficharge-profil/etablissement', views.afficharge_info_ecole, name='afficharge_info_ecole'),

     path('modification/<int:pk>/', views.modifier, name='modifier_info_ecole'),


]


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
   






]

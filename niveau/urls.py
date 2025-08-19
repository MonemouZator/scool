
from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [

    # autres modèles d'URL
    path('', views.niveau, name='niveau'),  # Assurez-vous que le nom correspond
    path('hjgfhk/',views.ajout,name='ajout-niveau'),# Chemin d'ajout  des informations
    path('niveau/',views.modifier,name='modifi-niveau'),# Chemin de modification  des informations
    path('supprime/<pk>/',views.supprimer_niveau,name='supprimer-niveau'),
   






]

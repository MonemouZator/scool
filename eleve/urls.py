
from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [

    # autres modèles d'URL
    path('eleve-gestion/', views.liste_totale_eleve, name='eleve'),  # Assurez-vous que le nom correspond
    path('fomecklghdpçupoidsupouigfdçufjqsojiduiiizyurgzeuruuygcwqzs',views.formeleve,name='forme'),
    path('fome-modif',views.forme_modifie,name='modif'),
    path('ajout/',views.ajout,name='ajout-eleve'),# Chemin d'ajout  des informations
     path('modifier_eleve/<int:pk>/', views.modifier, name='modifier_eleve'),# Chemin de modification  des informations
    path('sup/<pk>/',views.supprimer,name='supprimer-eleve'),
     path('eleve/<int:pk>/', views.detail_eleve, name='eleve_detail'),   # URL pour afficher le détail de l'élève
    path('configuration/',views.eleve_selection,name='configuration'),

    path('paiement/', views.effectuer_paiement, name='effectuer_paiement'),

    path('recu/<int:recu_id>/', views.afficher_recu, name='afficher_recu'),
    path('liste-eleves/', views.statut_paiement_eleve, name='liste_eleves'),
    path('eleve-par-niveau/',views.liste_eleves_par_niveau_annee, name='liste_eleves_par_niveau_annee'),
    path('liste-eleves-par-groupe/',views.liste_eleves_par_groupe, name='liste_eleves_par_groupe'),


]


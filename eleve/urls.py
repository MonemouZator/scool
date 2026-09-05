
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
    path('eleve/par/niveau/',views.liste_eleves_par_niveau_annee, name='liste_eleves_par_niveau'),
    path('liste/eleves/par/groupe/',views.liste_eleves_par_groupe, name='liste_eleves_par_groupe'),

    path('historique/',views.historique,name='historique_action'),
    path('profiles/comptable',views.profiles,name='profiles'),
    path('ajax/get_groupe/', views.get_groupe, name='get_groupe'),
    path('ajax/get_groupes/', views.get_groupes, name='get_groupes'),

    path('liste/statut/paiement', views.statut_paiement_eleve_fondateur, name='statut_paiement_eleve_fondateur'),
    path('eleve/niveau/',views.liste_eleves_niveau, name='liste_eleves_par_niveau_annee_fonda'),
    path('liste/eleves/classe/',views.liste_eleves_par_classe, name='liste_eleves_par_groupe_fonda'),
     path('eleve/fonda<int:pk>/', views.detail_eleves, name='eleve_detail_fonda'),
     path('ajax/get_groupe/', views.get_groupe, name='get_groupe'),

    # Formulaire de réinscription
    path('reinscription/', views.reinscription_eleve, name='reinscrire_eleve'),
    # AJAX pour remplir automatiquement les infos d'un élève par matricule
    path('ajax/get-eleve/', views.get_eleve_info, name='get_eleve_info'),
    # (optionnel) AJAX pour filtrer les groupes selon le niveau sélectionné
    path('ajax/get-groupes/', views.get_groupes, name='get_groupes'),

   # ==============================
# GESTION DES BADGES ÉLÈVES
# ==============================

path(
    'badges-eleves/',
    views.gestion_badges_eleves,
    name='gestion_badges_eleves'
),

path(
    'badge-eleve/<int:eleve_id>/',
    views.badge_eleve,
    name='badge_eleve'
),

path(
    'badges-eleves/impression/',
    views.badges_eleves_impression,
    name='badges_eleves_impression'
),

    
]


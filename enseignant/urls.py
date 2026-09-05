
from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [

    # autres modèles d'URL


    path('', views.maitre, name='enseignant'),  # Page d'accueil pour la gestion des enseignants
    path('enseignant/ajout/', views.ajout_enseignant, name='ajout_enseignant'),  # Ajouter un enseignant
    path('modifier/<int:id>/', views.modifier, name='modifier'),  # Modifier un enseignant
    path('supprime/<int:pk>/', views.supprim, name='supprimer-enseignant'),  # Supprimer un enseignant
    path('enseignant/<int:id>/', views.detail_enseignant, name='enseignant_detail'),  # Détails d'un enseignant
    path('paiement/', views.paiement_salaire, name='paiement_salaire'),  # Paiement des salaires
    path('depense/', views.ajouter_depense, name='depense'),  # Ajouter une dépense
    path('bilan-financier/', views.bilan_financier, name='bilan_financier'),  # Bilan financier
      # Bilan financier
    path('profil/enseignant',views.profi,name='profi_enseignant'),
    #path('profil/comptable',views.profil_comptable,name='profil_comptable'),
    path('supprimer-paiement/', views.supprimer_paiement, name='supprimer_paiement'),
    path('modifier-paiement/', views.modifier_paiement, name='modifier_paiement'),

    path('modifier-depense/', views.modifier_depense, name='modifier_depense'),
    path('supprimer-depense/', views.supprimer_depense, name='supprimer_depense'),
    path('ajouter-affectation/', views.ajouter_affectation_ajax, name='ajouter-affectation'),

    path('suivi/enseignant', views.suivi, name='suivie'),
   
    path('mot/passe', views.change_password, name='change_password'),

    path('historique/',views.historique_comptable,name='historique_Comptable'),

    path('ajax/get_classes_matiere/', views.get_classes_matiere, name='get_classes_matiere'),

    path('finance/finance/', views.finance, name='finance'),
    path('depense/fonda/', views.ajouter_depense_fondateur, name='depense_fondateur'),

    path('liste/enseignant/fonda/', views.enseignant_fondateur, name='enseignant_fonda'),
    path('paiement/fonda/', views.paiement_salaire_fonda, name='paiement_salaire_fonda'),

    path('suivi-matiere/enseigner', views.suivie_ensei, name='suivie_enseignant'),
    path('fondateur/enseignant/<int:id>/', views.detail_enseignant_fonda, name='detail_enseignant_fonda'),

   path('resultat-trimestriel/classe/enseigner', views.resultat_trimestriel_classe, name='resultat_trimestriel_classe'),
    path('bulletin-trimestriel/classe/enseigner', views.bulletin_trimestriel_enseignant, name='bulletin_trimestriel_classe'),
path(
    'badges-enseignants/',
    views.gestion_badges_enseignants,
    name='gestion_badges_enseignants'
),

path(
    'badge-enseignant/<int:enseignant_id>/',
    views.badge_enseignant,
    name='badge_enseignant'
),

path(
    'badges-enseignants/impression/',
    views.badges_enseignants_impression,
    name='badges_enseignants_impression'
),
]  





from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [

    # autres modèles d'URL


    path('', views.maitre, name='enseignant'),  # Page d'accueil pour la gestion des enseignants
    path('enseignant/', views.ajout, name='ajout-enseignant'),  # Ajouter un enseignant
    path('modifier/<int:id>/', views.modifier, name='modifier'),  # Modifier un enseignant
    path('supprime/<int:pk>/', views.supprim, name='supprimer-enseignant'),  # Supprimer un enseignant
    path('enseignant/<int:id>/', views.detail_enseignant, name='enseignant_detail'),  # Détails d'un enseignant
    path('paiement/', views.paiement_salaire, name='paiement_salaire'),  # Paiement des salaires
    path('depense/', views.ajouter_depense, name='depense'),  # Ajouter une dépense
    path('bilan-financier/', views.bilan_financier, name='bilan_financier'),  # Bilan financier
      # Bilan financier
    path('profil/',views.profi,name='profi'),
    path('supprimer-paiement/', views.supprimer_paiement, name='supprimer_paiement'),
    path('modifier-paiement/', views.modifier_paiement, name='modifier_paiement'),

    path('modifier-depense/', views.modifier_depense, name='modifier_depense'),
    path('supprimer-depense/', views.supprimer_depense, name='supprimer_depense'),

]  




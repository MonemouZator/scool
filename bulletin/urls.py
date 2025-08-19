from django.urls import path
from . import views

urlpatterns = [
    path('bulletins_trimestriels/', views.bulletins_trimestriels_niveau, name='bulletins_trimestriels'),  # Affiche la page des bulletins trimestriels
    # path('bulletins_annuels/', views.bulletin_annuel, name='bulletins_annuels'),  # Affiche la page des bulletins annuels
    path('bulletins-option/', views.bulletins_trimestriels_classe, name='bulletins_option'),  # Affiche l'option groupée pour les bulletins trimestriels
    path('resultat-groupe/', views.resultat_trimestriel_classe, name='resultat_groupe'),  # Affiche les résultats par groupe
    path('resultat-annuel-groupe/', views.resultat_annuel_classe, name='resultat_annuel'),  # Affiche les résultats annuels par groupe
    path('valider-bulletin-trimestre/', views.valider_bulletin_trimestre, name='trimestre'),  # Valide le bulletin trimestriel
    path('valider-bulletin-annuel/', views.valider_bulletin_annuel, name='valider_bulletin'),  # Valide le bulletin annuel
    path('resultats-trimestriels/', views.resultats_trimestriels_niveau, name='resultats_trimestriels'),
    path('resultats-annuels/', views.resultats_annuels_niveau, name='resultats_annuels'),

]

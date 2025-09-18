from django.urls import path
# Importation de la fonction definie dans la Wiew
from personnel import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),  # Redirige vers la vue de déconnexion,
    path('administrateurs/ajouter/', views.ajout_administrateur, name='ajouter_administrateur'),  # Vue pour ajouter un administrateur
    path('liste/', views.liste_administrateurs, name='liste_administrateurs'),  # Page pour afficher la liste des administrateurs

    path('administrateur/supprimer/<int:administrateur_id>/', views.supprimer_administrateur, name='supprimer_administrateur'),
    path('bloquer/<int:utilisateur_id>/', views.bloquer_utilisateur, name='bloquer_utilisateur'),
    path('debloquer/<int:utilisateur_id>/', views.debloquer_utilisateur, name='debloquer_utilisateur'),
    path('change-passe-word/', views.change_password, name='password_reset_request'),
    path('forgot-pwd/', views.forgot_pwd, name='forgot'),
    path('xoauth/<token>/change-pwd/',views.recover_pwd,name='change-pwd-email'),
    path('comptable-dashboard/', views.comptable_dashboard, name='comptable_dashboard'),
    path('enseignant-dashboard/', views.enseignant_dashboard, name='enseignant_dashboard'),
    # Ajoutez d'autres URL si nécessaire
    path('dashbord/',views.dashbord,name='fondateur.dashbord'),
     path('dashbord/directeur',views.dashbaord_fondateur,name='dashbaord.directeur'),
    path('aside/',views.bloc_aside,name='bloc_aside'),
    path('profil-utilisateur/',views.profil_user,name='profil'),
    path('bloquer/tous/utilisateurs/',views.bloquer_compte,name='bloquer_compte'),
    path('debloquer/tous/utilisateurs/',views.deloquer_compte,name='deloquer_compte'),
    path('historique/',views.historique,name='historique_action'),
    path('pwd/comptable',views.change_password_comptable,name='changer_password_comptable'),
    
]
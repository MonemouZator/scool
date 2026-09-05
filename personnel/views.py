from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from annee_scolaire.models import AnneeScolaire
from eleve.models import Eleve,EleveInscrit
from enseignant.models import Enseignant
from niveau.models import Niveau
from django.utils.timezone import now
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Administrateur
from django.db.models import Sum
from eleve.models import Recu
from datetime import date, datetime
from django.db.models import Sum,F
from eleve.models import FraisScolarite
from enseignant.models import Depense, PaiementSalaire
import json
import secrets
from .models import Administrateur, Token
from django.core.mail import EmailMessage
from django.conf import settings
from smtplib import SMTPException
from django.shortcuts import render
from .models import Historique


#################################################################
# Tableau de bord principal après connexion

@login_required
def home(request):
    services = request.session.get('services', [])

    # Récupération de la première année scolaire en cours (la plus récente)
    annee = AnneeScolaire.objects.filter(
        date_debut__lte=now().date(),
        date_fin__gte=now().date()
    ).order_by('-date_debut').first()

    nombre_eleves_par_annee = Eleve.objects.filter(
        annee_scolaire=annee,
        actif=True
    ).count() if annee else 0

    return render(request, 'base/index.html', {
        'services': services,
        'nombre_eleves_par_annee': nombre_eleves_par_annee,
        'annee_selectionnee': annee
    })

#################################################################
#FONCTION DE REDIRECTION VERS LES PAGES D'ACCUEILS DES UTILISATEURS 

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Veuillez entrer votre login et mot de passe.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # messages.success(request, "Bienvenue, vous êtes connecté avec succès.")

            fonction = user.fonction
            if fonction == 'COMPTABLE':

                return redirect('comptable_dashboard')
            
            elif fonction == 'ENSEIGNANT':

                return redirect('enseignant_dashboard')
            
            elif fonction in 'FONDATEUR':

                return redirect('dashbaord.directeur')
            
            elif fonction in 'DG':
                
                return redirect('fondateur.dashbord')
                
            else:
                messages.error(request, "Votre fonction est incorrecte ou manquante.")
                return redirect('login')
        else:
            messages.error(request, "Login ou mot de passe incorrect.")
            return redirect('login')

    return render(request, 'login/login.html')

#################################################################

#DECONNEXION LORSQU'UN UTILISATEUR EST CONNECTER
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirige vers la page de connexion après la déconnexion

#################################################################
#FONCTION D'ENREGISTREMENT DES UTILISATEURS

@login_required(login_url='/')
def ajout_administrateur(request):
    if request.method == "POST":
        username=request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get('cpwd')
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        telephone = request.POST.get("telephone")
        genre = request.POST.get("genre")
        date_naissance = request.POST.get("date_naissance")
        lieu_naiss = request.POST.get("lieu_naiss")
        fonction = request.POST.get("fonction")
        photo = request.FILES.get("photo")

        if Administrateur.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect("ajouter_administrateur")
        
        if Administrateur.objects.filter(telephone=telephone).exists():
            messages.error(request, "Ce numéro de téléphone est déjà utilisé par un autre utilisateur.")
            return redirect("ajouter_administrateur")

        
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne sont pas identiques.")
            return redirect('ajouter_administrateur')

        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect('ajouter_administrateur')
        
        if not any(char.isdigit() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins un chiffre.")
            return redirect('ajouter_administrateur')
        
        if not any(char.isalpha() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins une lettre.")
            return redirect('ajouter_administrateur')

        
        if Administrateur.objects.filter(username=username).exists():
            messages.error(request, "Cet identifiant existe déjà dans la base.")
            return redirect("ajouter_administrateur")
        
        if Administrateur.objects.filter(telephone=telephone).exists():
            messages.error(request, "Cet numero de téléphone est déjà utiliser .")
            return redirect("ajouter_administrateur")
        
        try:
            administrateur = Administrateur.objects.create(

                username=username,
                email=email,
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                genre=genre,
                date_naissance=date_naissance,
                lieu_naiss=lieu_naiss,
                fonction=fonction,
                photo=photo,
            )
            administrateur.set_password(password)
            administrateur.save()

            messages.success(request, "Compte creé avec succès !")
            return redirect("liste_administrateurs")
        except Exception as e:
            print("Erreur :", e)
            messages.error(request, f"Erreur lors de l'ajout : {e}")        

    return render(request, 'login/ajouter_administrateur.html')

#################################################################

#LISTE DES UTILISATEURS EXISTANTS
def liste_administrateurs(request):
    try:
        # Filtrer les administrateurs pour exclure les super utilisateurs
        administrateurs = Administrateur.objects.exclude(is_superuser=True)

        # Passer les administrateurs filtrés au template
        return render(request, 'login/liste_administrateurs.html', {'administrateurs': administrateurs})

    except Exception as e:
        # Gérer les erreurs et afficher un message si une exception se produit
        messages.error(request, f"Erreur lors du chargement des administrateurs : {e}")
        return render(request, 'login/liste_administrateurs.html', {'administrateurs': []})
    
#################################################################
##LA SUPPRESION DU COMPTE D'UN UTILISATEUR
def supprimer_administrateur(request, administrateur_id):
    administrateur = get_object_or_404(Administrateur, id=administrateur_id)
    administrateur.delete()
    messages.success(request, "Administrateur supprimé avec succès.")
    return redirect('liste_administrateurs')

#################################################################
#FONCTION POUR BLOGUER UN SEUL UTILISATEUR
@login_required(login_url='/')
def bloquer_utilisateur(request, utilisateur_id):  
     if request.user.is_authenticated and request.user.is_superuser:
        try:
            administrateur = Administrateur.objects.get(id=utilisateur_id)  # Assurez-vous d'utiliser Administrateur
            administrateur.is_active = False  # Bloquer l'utilisateur
            administrateur.save()

            messages.success(request, f"L'utilisateur {administrateur.username} a été bloqué avec succès.")
        except Administrateur.DoesNotExist:
            messages.error(request, "Administrateur non trouvé.")

            return redirect(reverse('user-settings', args=[utilisateur_id]))
     return redirect('liste_administrateurs')

#################################################################

# #DEBLOQUER UN UTILISATEUR
@login_required(login_url='/')
def debloquer_utilisateur(request, utilisateur_id):
     
     if request.user.is_authenticated and request.user.is_superuser:

        try:
            administrateur = Administrateur.objects.get(id=utilisateur_id)  # Assurez-vous d'utiliser Administrateur
            administrateur.is_active = True  # Bloquer l'utilisateur
            administrateur.save()

            messages.success(request, f"L'utilisateur {administrateur.username} a été bloqué avec succès.")
        except Administrateur.DoesNotExist:
            messages.error(request, "Administrateur non trouvé.")

            return redirect(reverse('user-settings', args=[utilisateur_id]))
     return redirect('liste_administrateurs')

#################################################################
# bloquage de tous les comptes utilisateurs
@login_required(login_url='/')
def bloquer_compte(request):
    if request.user.is_authenticated and request.user.is_superuser:
        users = User.objects.all().exclude(username=request.user.username)
        for user in users:
            user.is_active = False
            user.save()
        return redirect('liste_administrateurs')
    return redirect('logout')

#################################################################
# debloquer tous les comptes utilsateurs
@login_required(login_url='/')
def deloquer_compte(request):
    if request.user.is_authenticated and request.user.is_superuser:
        users = User.objects.all().exclude(username=request.user.username)
        for user in users:
            user.is_active = True
            user.save()
        return redirect('liste_administrateurs')
    return redirect('logout')

#################################################################

#LES TABLEAUX DE BORD DES DIFFERENTS UTILISATEURS CONCERNES

# =========================================================
# TABLEAU DE BORD DU COMPTABLE
# =========================================================

@login_required
def comptable_dashboard(request):

    # -----------------------------------------------------
    # SERVICES DE L'UTILISATEUR
    # -----------------------------------------------------

    services = request.session.get('services', [])


    # -----------------------------------------------------
    # ANNÉE SCOLAIRE EN COURS
    # -----------------------------------------------------

    annee_selectionnee = (
        AnneeScolaire.objects
        .filter(
            date_debut__lte=date.today(),
            date_fin__gte=date.today()
        )
        .first()
    )


    # -----------------------------------------------------
    # NOMBRE D'ÉLÈVES
    #
    # IMPORTANT :
    # On utilise maintenant EleveInscrit.
    # -----------------------------------------------------

    if annee_selectionnee:

        nombre_eleves_par_annee = (
            EleveInscrit.objects
            .filter(
                annee_scolaire=annee_selectionnee
            )
            .values('eleve')
            .distinct()
            .count()
        )

    else:

        nombre_eleves_par_annee = 0


    # -----------------------------------------------------
    # NOMBRE D'ENSEIGNANTS
    # -----------------------------------------------------

    nombre_enseignants = Enseignant.objects.count()


    # -----------------------------------------------------
    # NOMBRE DE NIVEAUX
    # -----------------------------------------------------

    nombre_niveaux = Niveau.objects.count()


    # -----------------------------------------------------
    # NOMBRE D'UTILISATEURS
    # -----------------------------------------------------

    User = get_user_model()

    nombre_utilisateurs = User.objects.count()


    # =====================================================
    # GRAPHIQUE DES PAIEMENTS
    # =====================================================

    labels = []

    data = []


    mois_fr = [
        "",
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre"
    ]


    # -----------------------------------------------------
    # PAIEMENTS DE L'ANNÉE SCOLAIRE SÉLECTIONNÉE
    # -----------------------------------------------------

    if annee_selectionnee:

        paiements_par_mois = (
            Recu.objects
            .filter(
                frais_scolarite__annee_scolaire=annee_selectionnee
            )
            .values(
                'date_recu__month'
            )
            .annotate(
                total=Sum('montant')
            )
            .order_by(
                'date_recu__month'
            )
        )


        # -------------------------------------------------
        # DICTIONNAIRE DES PAIEMENTS
        # -------------------------------------------------

        mois_dict = {
            item['date_recu__month']: item['total']
            for item in paiements_par_mois
        }


        # -------------------------------------------------
        # PRÉPARATION DU GRAPHIQUE
        # -------------------------------------------------

        for month in range(1, 13):

            labels.append(
                mois_fr[month]
            )

            data.append(
                float(
                    mois_dict.get(month, 0)
                )
            )


    # -----------------------------------------------------
    # SI AUCUNE ANNÉE SCOLAIRE
    # -----------------------------------------------------

    else:

        labels = mois_fr[1:]

        data = [0] * 12


    # =====================================================
    # CONTEXTE
    # =====================================================

    context = {

        'services': services,

        'annee_selectionnee': annee_selectionnee,

        'nombre_eleves_par_annee': nombre_eleves_par_annee,

        'nombre_enseignants': nombre_enseignants,

        'nombre_niveaux': nombre_niveaux,

        'nombre_utilisateurs': nombre_utilisateurs,

        'labels': json.dumps(labels),

        'data': json.dumps(data),
    }


    # =====================================================
    # AFFICHAGE
    # =====================================================

    return render(
        request,
        'login/comptable_dashboard.html',
        context
    )



#############################################
# TABLEAUX DE BORD DE enseignants
#############################################


@login_required
def enseignant_dashboard(request):

    services = request.session.get('services', [])

    # ==========================================================
    # ANNÉE SCOLAIRE ACTIVE
    # ==========================================================
    try:
        annee = AnneeScolaire.objects.get(
            date_debut__lte=now().date(),
            date_fin__gte=now().date()
        )
    except AnneeScolaire.DoesNotExist:
        annee = None

    # ==========================================================
    # NOMBRE TOTAL D'ÉLÈVES
    # ==========================================================
    if annee:
        nombre_eleves_par_annee = (
            EleveInscrit.objects
            .filter(
                annee_scolaire=annee,
                actif=True,
                eleve__actif=True
            )
            .values('eleve')
            .distinct()
            .count()
        )
    else:
        nombre_eleves_par_annee = 0

    # ==========================================================
    # NIVEAUX AVEC EFFECTIFS
    # ==========================================================
    if annee:
        niveaux_avec_effectifs = (
            Niveau.objects
            .annotate(
                nombre_eleves=Count(
                    'eleveinscrit',
                    filter=Q(
                        eleveinscrit__annee_scolaire=annee,
                        eleveinscrit__actif=True,
                        eleveinscrit__eleve__actif=True
                    ),
                    distinct=True
                )
            )
            .order_by('nom')
        )
    else:
        niveaux_avec_effectifs = (
            Niveau.objects
            .annotate(
                nombre_eleves=Count(
                    'eleveinscrit',
                    filter=Q(
                        eleveinscrit__actif=True,
                        eleveinscrit__eleve__actif=True
                    ),
                    distinct=True
                )
            )
            .order_by('nom')
        )

    # ==========================================================
    # AUTRES COMPTEURS
    # ==========================================================
    nombre_enseignants = Enseignant.objects.count()

    nombre_niveaux = Niveau.objects.count()

    User = get_user_model()
    nombre_utilisateurs = User.objects.count()

    # ==========================================================
    # CONTEXTE
    # ==========================================================
    context = {
        'services': services,

        'annee_selectionnee': annee,

        'nombre_eleves_par_annee': nombre_eleves_par_annee,

        'nombre_enseignants': nombre_enseignants,

        'nombre_niveaux': nombre_niveaux,

        'nombre_utilisateurs': nombre_utilisateurs,

        'niveaux_avec_effectifs': niveaux_avec_effectifs,
    }

    return render(
        request,
        'login/enseignant_dashboard.html',
        context
    )


##############################################################
# TABLEAU DE BORD DU DIRECTEUR
##############################################################

from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now

from annee_scolaire.models import AnneeScolaire
from niveau.models import Niveau
from enseignant.models import Enseignant
from eleve.models import EleveInscrit


@login_required
def dashbord(request):

    services = request.session.get('services', [])

    # ==========================================================
    # ANNÉE SCOLAIRE EN COURS
    # ==========================================================

    annee = (
        AnneeScolaire.objects
        .filter(
            date_debut__lte=now().date(),
            date_fin__gte=now().date()
        )
        .order_by('-date_debut')
        .first()
    )

    # ==========================================================
    # NOMBRE TOTAL D'ÉLÈVES INSCRITS POUR L'ANNÉE EN COURS
    # ==========================================================

    if annee:

        nombre_eleves_par_annee = (
            EleveInscrit.objects
            .filter(
                annee_scolaire=annee,
                actif=True
            )
            .count()
        )

    else:

        nombre_eleves_par_annee = 0

    # ==========================================================
    # TOUS LES NIVEAUX + EFFECTIF DES ÉLÈVES INSCRITS
    # ==========================================================

    if annee:

        niveaux_avec_effectifs = (
            Niveau.objects
            .annotate(
                nombre_eleves=Count(
                    'eleveinscrit',
                    filter=Q(
                        eleveinscrit__annee_scolaire=annee,
                        eleveinscrit__actif=True
                    )
                )
            )
            .order_by('nom')
        )

    else:

        niveaux_avec_effectifs = (
            Niveau.objects
            .annotate(
                nombre_eleves=Count(
                    'eleveinscrit'
                )
            )
            .order_by('nom')
        )

    # ==========================================================
    # NOMBRE D'ENSEIGNANTS
    # ==========================================================

    nombre_enseignants = Enseignant.objects.count()

    # ==========================================================
    # NOMBRE DE NIVEAUX
    # ==========================================================

    nombre_niveaux = Niveau.objects.count()

    # ==========================================================
    # NOMBRE D'UTILISATEURS
    # ==========================================================

    User = get_user_model()

    nombre_utilisateurs = User.objects.count()

    # ==========================================================
    # CONTEXTE
    # ==========================================================

    context = {
        'services': services,

        'annee_selectionnee': annee,

        'nombre_eleves_par_annee': nombre_eleves_par_annee,

        'niveaux_avec_effectifs': niveaux_avec_effectifs,

        'nombre_enseignants': nombre_enseignants,

        'nombre_niveaux': nombre_niveaux,

        'nombre_utilisateurs': nombre_utilisateurs,
    }

    return render(
        request,
        'login/index.html',
        context
    )
######################################################
# TABLEAU DE BORD DU FONDATEUR
######################################################

@login_required
def dashbaord_fondateur(request):

    services = request.session.get('services', [])

    # ==========================================================
    # ANNÉE SCOLAIRE EN COURS
    # ==========================================================
    annee_selectionnee = (
        AnneeScolaire.objects
        .filter(
            date_debut__lte=date.today(),
            date_fin__gte=date.today()
        )
        .first()
    )

    # ==========================================================
    # NOMBRE D'ÉLÈVES INSCRITS
    # ==========================================================
    if annee_selectionnee:

        nombre_eleves_par_annee = (
            EleveInscrit.objects
            .filter(
                annee_scolaire=annee_selectionnee,
                actif=True,
                eleve__actif=True
            )
            .values('eleve')
            .distinct()
            .count()
        )

    else:
        nombre_eleves_par_annee = 0

    # ==========================================================
    # EFFECTIFS PAR NIVEAU
    # ==========================================================
    niveaux_avec_effectifs = []

    if annee_selectionnee:

        niveaux = Niveau.objects.all().order_by('nom')

        for niveau in niveaux:

            effectif = (
                EleveInscrit.objects
                .filter(
                    annee_scolaire=annee_selectionnee,
                    niveau=niveau,
                    actif=True,
                    eleve__actif=True
                )
                .values('eleve')
                .distinct()
                .count()
            )

            niveau.nombre_eleves = effectif

            niveaux_avec_effectifs.append(niveau)

    else:

        niveaux = Niveau.objects.all().order_by('nom')

        for niveau in niveaux:
            niveau.nombre_eleves = 0
            niveaux_avec_effectifs.append(niveau)

    # ==========================================================
    # STATISTIQUES GÉNÉRALES
    # ==========================================================
    nombre_enseignants = Enseignant.objects.count()

    nombre_niveaux = Niveau.objects.count()

    User = get_user_model()

    nombre_utilisateurs = User.objects.count()

    # ==========================================================
    # INITIALISATION DES DONNÉES FINANCIÈRES
    # ==========================================================
    total_entree = 0
    total_sortie = 0
    solde_net = 0
    total_impaye = 0

    total_sorties_salaire = 0
    total_sorties_depense = 0

    # ==========================================================
    # STATISTIQUES FINANCIÈRES
    # ==========================================================
    if annee_selectionnee:

        # ------------------------------------------------------
        # TOTAL DES ENTRÉES
        # Paiements scolaires
        # ------------------------------------------------------
        total_entree = (
            FraisScolarite.objects
            .filter(
                annee_scolaire=annee_selectionnee
            )
            .aggregate(
                total=Sum('total_paye')
            )['total'] or 0
        )

        # ------------------------------------------------------
        # SALAIRES
        # ------------------------------------------------------
        total_sorties_salaire = (
            PaiementSalaire.objects
            .filter(
                annee_scolaire=annee_selectionnee
            )
            .aggregate(
                total=Sum('montant')
            )['total'] or 0
        )

        # ------------------------------------------------------
        # AUTRES DÉPENSES
        # ------------------------------------------------------
        total_sorties_depense = (
            Depense.objects
            .filter(
                annee_scolaire=annee_selectionnee
            )
            .aggregate(
                total=Sum('montant')
            )['total'] or 0
        )

        # ------------------------------------------------------
        # TOTAL DES SORTIES
        # ------------------------------------------------------
        total_sortie = (
            total_sorties_salaire
            + total_sorties_depense
        )

        # ------------------------------------------------------
        # SOLDE NET
        # ------------------------------------------------------
        solde_net = total_entree - total_sortie

        # ------------------------------------------------------
        # TOTAL IMPAYÉ
        # ------------------------------------------------------
        total_impaye = (
            FraisScolarite.objects
            .filter(
                annee_scolaire=annee_selectionnee
            )
            .aggregate(
                total=Sum(
                    F('montant_total') - F('total_paye')
                )
            )['total'] or 0
        )

    # ==========================================================
    # GRAPHIQUE DES PAIEMENTS PAR MOIS
    # ==========================================================
    labels = []
    data = []

    mois_fr = [
        "",
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre"
    ]

    if annee_selectionnee:

        paiements_par_mois = (
            Recu.objects
            .filter(
                frais_scolarite__annee_scolaire=annee_selectionnee
            )
            .values(
                'date_recu__month'
            )
            .annotate(
                total=Sum('montant')
            )
            .order_by(
                'date_recu__month'
            )
        )

        mois_dict = {
            item['date_recu__month']: item['total']
            for item in paiements_par_mois
        }

        for month in range(1, 13):

            labels.append(
                mois_fr[month]
            )

            data.append(
                float(
                    mois_dict.get(month, 0)
                )
            )

    else:

        labels = mois_fr[1:]
        data = [0] * 12

    # ==========================================================
    # CONTEXTE
    # ==========================================================
    context = {

        'services': services,

        # Année
        'annee_selectionnee':
            annee_selectionnee,

        # Élèves
        'nombre_eleves_par_annee':
            nombre_eleves_par_annee,

        # Effectifs par niveau
        'niveaux_avec_effectifs':
            niveaux_avec_effectifs,

        # Statistiques générales
        'nombre_enseignants':
            nombre_enseignants,

        'nombre_niveaux':
            nombre_niveaux,

        'nombre_utilisateurs':
            nombre_utilisateurs,

        # Graphique
        'labels':
            json.dumps(labels),

        'data':
            json.dumps(data),

        # Finances
        'total_entree':
            total_entree,

        'total_sortie':
            total_sortie,

        'solde_net':
            solde_net,

        'total_impaye':
            total_impaye,

        'total_sorties_salaire':
            total_sorties_salaire,

        'total_sorties_depense':
            total_sorties_depense,
    }

    return render(
        request,
        'login/dashbaord_fondateur.html',
        context
    )





#################################################################
   
def bloc_aside(request):

    return render(request,'base/base.html')

#################################################################
#PROFIL ET CHANGEMENTS DES INFORMATION DE L'UTILISATEUR CONNECTER
#################################################################

@login_required
def profil_user(request):
    user = request.user  # Utilisateur connecté

    if request.method == "POST":
        user.nom = request.POST.get("nom", user.nom)
        user.prenom = request.POST.get("prenom", user.prenom)
        user.email = request.POST.get("email", user.email)
        user.genre = request.POST.get("sexe", user.genre)
        user.telephone = request.POST.get("contact", user.telephone)
        user.lieu_naiss = request.POST.get("filiation", user.lieu_naiss)
        user.username = request.POST.get("username", user.username)  # Optionnel

        date_str = request.POST.get("date")
        if date_str:
            try:
                user.date_naissance = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Format de date invalide. Utilise AAAA-MM-JJ.")

        # Gestion de la photo
        if "photo" in request.FILES:
            user.photo = request.FILES["photo"]

        try:
            user.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la sauvegarde : {e}")

        return redirect("profil")

    return render(request, "login/profil.html", {"user": user})

#################################################################
#FONCTION DE CHANGEMENT DE MOT DE PASSE DE L'UTILISATEUR COURANT
#################################################################

@login_required(login_url='/')
def change_password(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('cpwd')
        auto_login = request.POST.get('connect')  # checkbox pour rester connecté

        # Vérifications côté serveur
        if not password or not confirm_password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('password_reset_request')

        if password != confirm_password:
            messages.error(request, "Les mots de passe ne sont pas identiques.")
            return redirect('password_reset_request')

        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect('password_reset_request')
        
        if not any(char.isdigit() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins un chiffre.")
            return redirect('password_reset_request')
        
        if not any(char.isalpha() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins une lettre.")
            return redirect('password_reset_request')

        # Changement du mot de passe
        user = request.user
        user.set_password(password)
        user.save()

        # Option : reconnecter l'utilisateur
        if auto_login == "on":
            user = authenticate(username=user.username, password=password)
            if user is not None:
                login(request, user)
            messages.success(request, "Mot de passe changé avec succès, vous êtes reconnecté !")
            return redirect('password_reset_request')
        else:
            logout(request)
            messages.success(request, "Mot de passe changé, veuillez vous reconnecter.")
            return redirect('login')
    return render(request, 'login/recover_password.html')

#################################################################
#FONCTION DE CHANGEMENT DE MOT DE PASSE PAR MAIL
#################################################################

User = get_user_model()

def forgot_pwd(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            # Générer le token
            token = secrets.token_urlsafe(32)
            Token.objects.create(user=user, token=token)

            # Construire l'URL de réinitialisation
            # url = f"http://localhost:8000/xoauth/{token}/change-pwd/"
            url = f"https://ecole-bnb.onrender.com/xoauth/{token}/change-pwd/"

            # Préparer et envoyer l'email
            subject = "Changement de mot de passe"
            message = f"Bonjour {user.get_full_name()},\n\nCliquez sur ce lien pour changer votre mot de passe :\n{url}\n\nSi vous n'avez pas fait cette demande, ignorez cet e-mail."

            email_from = settings.EMAIL_HOST_USER
            email_msg = EmailMessage(subject, message, email_from, [email])
            email_msg.send()

            context = {
                "message": "Un lien de changement de mot de passe a été envoyé à votre adresse e-mail."
            }
            return render(request, 'login/forgot_pwd.html', context)

        except User.DoesNotExist:
            # Aucun utilisateur trouvé avec cet email
            context = {
                "error": "L'adresse e-mail saisie n'existe pas dans notre système."
            }
            return render(request, 'login/forgot_pwd.html', context)

    return render(request, 'login/forgot_pwd.html')

#################################################################
def recover_pwd(request, token):
    token_obj = Token.objects.filter(token=token).first()
    if not token_obj:
        return render(request, 'login/change_pwd.html', {"error": "Ce lien n'est plus valable"})

    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not password or not confirm_password:
            return render(request, 'login/change_pwd.html', {"error": "Veuillez remplir tous les champs."})

        if password != confirm_password:
            return render(request, 'login/change_pwd.html', {"error": "Les mots de passe ne correspondent pas."})

        user = get_object_or_404(User, id=token_obj.user.id)
        user.set_password(password)
        user.save()

        token_obj.delete()

        logout(request)

        return redirect('login')

    # GET request : affichage du formulaire
    return render(request, 'login/change_pwd.html')

#################################################################

@login_required(login_url='/')
def historique(request):
    
    if request.user.is_superuser:
        # Super utilisateur : voir tous les historiques
        historiques = Historique.objects.all().order_by('-created_time')
    else:
        # Utilisateur normal : voir uniquement ses propres actions
        historiques = Historique.objects.filter(user=request.user).order_by('-created_time')

    return render(request, 'login/historique.html', {'historiques': historiques})

#################################################################

@login_required(login_url='/')
def change_password_comptable(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('cpwd')
        auto_login = request.POST.get('connect')  # checkbox pour rester connecté

        # Vérifications côté serveur
        if not password or not confirm_password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('password_reset_request')

        if password != confirm_password:
            messages.error(request, "Les mots de passe ne sont pas identiques.")
            return redirect('password_reset_request')

        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect('password_reset_request')
        
        if not any(char.isdigit() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins un chiffre.")
            return redirect('password_reset_request')
        
        if not any(char.isalpha() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins une lettre.")
            return redirect('password_reset_request')

        # Changement du mot de passe
        user = request.user
        user.set_password(password)
        user.save()

        # Option : reconnecter l'utilisateur
        if auto_login == "on":
            user = authenticate(username=user.username, password=password)
            if user is not None:
                login(request, user)
            messages.success(request, "Mot de passe changé avec succès, vous êtes reconnecté !")
            return redirect('password_reset_request')
        else:
            logout(request)
            messages.success(request, "Mot de passe changé, veuillez vous reconnecter.")
            return redirect('login')
    return render(request, 'login/changer_password_comptable.html')

#################################################################

@login_required(login_url='/')
def changer_password_admin(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('cpwd')
        auto_login = request.POST.get('connect')  # checkbox pour rester connecté

        # Vérifications côté serveur
        if not password or not confirm_password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('changer_password_admin')

        if password != confirm_password:
            messages.error(request, "Les mots de passe ne sont pas identiques.")
            return redirect('changer_password_admin')

        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect('changer_password_admin')
        
        if not any(char.isdigit() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins un chiffre.")
            return redirect('changer_password_admin')
        
        if not any(char.isalpha() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins une lettre.")
            return redirect('changer_password_admin')

        # Changement du mot de passe
        user = request.user
        user.set_password(password)
        user.save()

        # Option : reconnecter l'utilisateur
        if auto_login == "on":
            user = authenticate(username=user.username, password=password)
            if user is not None:
                login(request, user)
            messages.success(request, "Mot de passe changé avec succès, vous êtes reconnecté !")
            return redirect('changer_password_admin')
        else:
            logout(request)
            messages.success(request, "Mot de passe changé, veuillez vous reconnecter.")
            return redirect('login')
    return render(request, 'admin/changer_password_admin.html')

#################################################################

@login_required(login_url='')
def profil_admin(request):

    user = request.user  # Utilisateur connecté

    if request.method == "POST":
        user.nom = request.POST.get("nom", user.nom)
        user.prenom = request.POST.get("prenom", user.prenom)
        user.email = request.POST.get("email", user.email)
        user.genre = request.POST.get("sexe", user.genre)
        user.telephone = request.POST.get("contact", user.telephone)
        user.lieu_naiss = request.POST.get("filiation", user.lieu_naiss)
        user.username = request.POST.get("username", user.username)  # Optionnel

        date_str = request.POST.get("date")
        if date_str:
            try:
                user.date_naissance = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Format de date invalide. Utilise AAAA-MM-JJ.")

        # Gestion de la photo
        if "photo" in request.FILES:
            user.photo = request.FILES["photo"]

        try:
            user.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la sauvegarde : {e}")

        return redirect("profil_admin")
    
    context = {
        "user": user,
    }
    return render(request,'admin/profil_admin.html',context)

#################################################################
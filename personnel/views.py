from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from annee_scolaire.models import AnneeScolaire
from eleve.models import Eleve
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

# TABLEAUX DE BORD DU COMPTABLE
@login_required
def comptable_dashboard(request):
    services = request.session.get('services', [])
    annee_selectionnee = AnneeScolaire.objects.filter(date_debut__lte=date.today(), date_fin__gte=date.today()).first()

    if annee_selectionnee:
        nombre_eleves_par_annee = Eleve.objects.filter(annee_scolaire=annee_selectionnee).count()
    else:
        nombre_eleves_par_annee = 0

    nombre_enseignants = Enseignant.objects.count()
    nombre_niveaux = Niveau.objects.count()
    User = get_user_model()
    nombre_utilisateurs = User.objects.count()

    #Préparer les données du graphique
    labels = []
    data = []

    mois_fr = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    if annee_selectionnee:
        # Filtrer les paiements pour l'année sélectionnée
        paiements_par_mois = (
            Recu.objects
            .filter(date_recu__gte=datetime(annee_selectionnee.date_debut.year, 1, 1), 
                    date_recu__lt=datetime(annee_selectionnee.date_fin.year + 1, 1, 1))
            .values('date_recu__month')  # Grouper par mois
            .annotate(total=Sum('montant'))
            .order_by('date_recu__month')
        )

        # Créer un dictionnaire avec les mois et le total des paiements
        mois_dict = {item['date_recu__month']: item['total'] for item in paiements_par_mois}

        # Préparer les labels et les données à afficher
        for month in range(1, 13):
            labels.append(mois_fr[month])  # Utiliser le mois en français
            # Convertir le montant en float pour éviter l'erreur de sérialisation
            data.append(float(mois_dict.get(month, 0)))  # Ajouter 0 si aucun paiement pour ce mois

        # Affichage pour le débogage
        print("Labels:", labels)
        print("Data:", data)

    # Contexte à envoyer au template
    context = {
        'services': services,
        'annee_selectionnee': annee_selectionnee,
        'nombre_eleves_par_annee': nombre_eleves_par_annee,
        'nombre_enseignants': nombre_enseignants,
        'nombre_niveaux': nombre_niveaux,
        'nombre_utilisateurs': nombre_utilisateurs,
        'labels': json.dumps(labels),  # Convertir labels en JSON
        'data': json.dumps(data),  # Convertir data en JSON
    }

    return render(request, 'login/comptable_dashboard.html', context)

#############################################
# TABLEAUX DE BORD DE DIRECTEUR
#############################################

@login_required
def enseignant_dashboard(request):
    services = request.session.get('services', [])
    try:
        annee = AnneeScolaire.objects.get(
            date_debut__lte=now().date(),
            date_fin__gte=now().date()
        )
    except AnneeScolaire.DoesNotExist:
        annee = None
    # Nombre total d'élèves
    if annee:
        nombre_eleves_par_annee = Eleve.objects.filter(
            annee_scolaire=annee, actif=True
        ).count()
    else:
        nombre_eleves_par_annee = 0
    # ✅ Tous les niveaux avec nombre d'élèves
    niveaux_avec_effectifs = (
        Niveau.objects
        .annotate(
            nombre_eleves=Count(
                'eleve',
                filter=Q(eleve__annee_scolaire=annee, eleve__actif=True)
            )
        )
        .order_by('nom')
    )
    # Autres compteurs
    nombre_enseignants = Enseignant.objects.count()
    nombre_niveaux = Niveau.objects.count()
    User = get_user_model()
    nombre_utilisateurs = User.objects.count()
    context = {
        'services': services,
        'annee_selectionnee': annee,
        'nombre_eleves_par_annee': nombre_eleves_par_annee,
        'nombre_enseignants': nombre_enseignants,
        'nombre_niveaux': nombre_niveaux,
        'nombre_utilisateurs': nombre_utilisateurs,
        'niveaux_avec_effectifs': niveaux_avec_effectifs,  # ✅ clé pour cartes
    }
    return render(request, 'login/enseignant_dashboard.html', context)

##############################################################   
#TABLEAU DE BORD DU DIRECTEUR
##############################################################
from django.db.models import Count, Q
# TABLEAU DE BORD DU DIRECTEUR
@login_required
def dashbord(request):
    services = request.session.get('services', [])
    annee = AnneeScolaire.objects.filter(
        date_debut__lte=now().date(),
        date_fin__gte=now().date()
    ).order_by('-date_debut').first()
    # Nombre total d'élèves
    if annee:
        nombre_eleves_par_annee = Eleve.objects.filter(
            annee_scolaire=annee, actif=True
        ).count()
    else:
        nombre_eleves_par_annee = 0
    # ✅ TOUS LES NIVEAUX + COMPTE DES ÉLÈVES
    niveaux_avec_effectifs = (
        Niveau.objects
        .annotate(
            nombre_eleves=Count(
                'eleve',
                filter=Q(eleve__annee_scolaire=annee, eleve__actif=True)
            )
        )
        .order_by('nom')
    )
    nombre_enseignants = Enseignant.objects.count()
    nombre_niveaux = Niveau.objects.count()
    User = get_user_model()
    nombre_utilisateurs = User.objects.count()
    context = {
        'services': services,
        'annee_selectionnee': annee,
        'nombre_eleves_par_annee': nombre_eleves_par_annee,
        'niveaux_avec_effectifs': niveaux_avec_effectifs,  # ✅ clé
        'nombre_enseignants': nombre_enseignants,
        'nombre_niveaux': nombre_niveaux,
        'nombre_utilisateurs': nombre_utilisateurs,
    }
    return render(request, 'login/index.html', context)

######################################################
# TABLEAUX DE BORD DU FONDATEUR
######################################################

@login_required
def dashbaord_fondateur(request):
    services = request.session.get('services', [])

    # Déterminer l'année scolaire sélectionnée ou en cours
    annee_selectionnee = AnneeScolaire.objects.filter(
        date_debut__lte=date.today(),
        date_fin__gte=date.today()
    ).first()

    # Nombre d'élèves
    nombre_eleves_par_annee = (
        Eleve.objects.filter(annee_scolaire=annee_selectionnee).count()
        if annee_selectionnee else 0
    )

    # Statistiques générales
    nombre_enseignants = Enseignant.objects.count()
    nombre_niveaux = Niveau.objects.count()
    User = get_user_model()
    nombre_utilisateurs = User.objects.count()

    # Initialiser les totaux financiers
    total_entree = total_sortie = solde_net = total_impaye = 0

    if annee_selectionnee:
        # Total des paiements effectués par les élèves
        total_entree = FraisScolarite.objects.filter(
            annee_scolaire=annee_selectionnee
        ).aggregate(total=Sum('total_paye'))['total'] or 0

        # Total des salaires versés
        total_sorties_salaire = PaiementSalaire.objects.filter(
            annee_scolaire=annee_selectionnee
        ).aggregate(total=Sum('montant'))['total'] or 0

        # Total des autres dépenses
        total_sorties_depense = Depense.objects.filter(
            annee_scolaire=annee_selectionnee
        ).aggregate(total=Sum('montant'))['total'] or 0

        total_sortie = total_sorties_salaire + total_sorties_depense
        solde_net = total_entree - total_sortie

        # Total impayé réel
        total_impaye = FraisScolarite.objects.filter(
            annee_scolaire=annee_selectionnee
        ).aggregate(total=Sum(F('montant_total') - F('total_paye')))['total'] or 0

    # Préparer les données du graphique mensuel
    labels = []
    data = []
    mois_fr = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
               "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    if annee_selectionnee:
        paiements_par_mois = (
            Recu.objects
            .filter(
                date_recu__gte=datetime(annee_selectionnee.date_debut.year, 1, 1),
                date_recu__lt=datetime(annee_selectionnee.date_fin.year + 1, 1, 1)
            )
            .values('date_recu__month')
            .annotate(total=Sum('montant'))
            .order_by('date_recu__month')
        )
        mois_dict = {item['date_recu__month']: item['total'] for item in paiements_par_mois}
        for month in range(1, 13):
            labels.append(mois_fr[month])
            data.append(float(mois_dict.get(month, 0)))

    context = {
        'services': services,
        'annee_selectionnee': annee_selectionnee,
        'nombre_eleves_par_annee': nombre_eleves_par_annee,
        'nombre_enseignants': nombre_enseignants,
        'nombre_niveaux': nombre_niveaux,
        'nombre_utilisateurs': nombre_utilisateurs,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'total_entree': total_entree,
        'total_sortie': total_sortie,
        'solde_net': solde_net,
        'total_impaye': total_impaye,
    }

    return render(request, 'login/dashbaord_fondateur.html', context)

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
            url = f"http://localhost:8000/xoauth/{token}/change-pwd/"

            # Préparer et envoyer l'email
            subject = "Changement de mot de passe"
            message = f"Bonjour {user.get_full_name()},\n\nCliquez sur ce lien pour changer votre mot de passe :\n{url}\n\nSi vous n'avez pas fait cette demande, ignorez cet e-mail."
            email_from = settings.EMAIL_HOST_USER
            email_msg = EmailMessage(subject, message, email_from, [email])
            email_msg.send()

            context = {"message": True}
            return render(request, 'login/forgot_pwd.html', context)

        except User.DoesNotExist:
            # Aucun utilisateur trouvé avec cet email
            context = {"error": True}
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
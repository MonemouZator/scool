from django.shortcuts import render,redirect,get_object_or_404
from enseignant.models import Enseignant,PaiementSalaire
from django.shortcuts import render, redirect
from .models import Depense
from django.contrib import messages
from eleve .models import Eleve , FraisScolarite,EleveInscrit
from annee_scolaire.models import AnneeScolaire
from personnel.models import Administrateur
from django.db.models import Sum,Avg
from django.db import models  # Importation de models
from datetime import datetime
from matiere.models import EnseignantMatiere
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from personnel.models import Historique, Administrateur
from note.models import Note


# --- LISTE DES ENSEIGNANTS ---
def maitre(request):
    enseignants = Enseignant.objects.all()
    niveaux = Niveau.objects.all()
    groupes = GroupeClasse.objects.all()
    matieres = Matiere.objects.all()

    context = {
        'enseignants': enseignants,
        'niveaux': niveaux,
        'groupes': groupes,
        'matieres': matieres,
    }
    return render(request, 'base/pages/tables/data.html', context)

# --- AJOUT D'UN ENSEIGNANT ---
def ajout_enseignant(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        telephone = request.POST.get("telephone")
        genre = request.POST.get("sexe")
        date_naissance = request.POST.get("date_naissance")
        lieu_naiss = request.POST.get("lieu_naiss")
        specialite = request.POST.get("specialite")
        adresse = request.POST.get("adresse")
        photo = request.FILES.get("photo")

        # Vérification date
        try:
            date_naissance = datetime.strptime(date_naissance, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Date de naissance invalide.")
            return redirect("enseignant")

        # Vérification si username ou email existe déjà
        if Administrateur.objects.filter(username=username).exists():
            messages.error(request, " Ce nom d’utilisateur est déjà utilisé.")
            return redirect("enseignant")
        
        if Administrateur.objects.filter(telephone=telephone).exists():
            messages.error(request, "Ce numéro de téléphone est déjà utilisé par un autre utilisateur.")
            return redirect("enseignant")

        if Administrateur.objects.filter(email=email).exists():
            messages.error(request, "Email déjà utilisé.")
            return redirect("enseignant")
        
        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect('enseignant')
        
        if not any(char.isdigit() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins un chiffre.")
            return redirect('enseignant')
        
        if not any(char.isalpha() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins une lettre.")
            return redirect('enseignant')

        try:
            # Créer l'utilisateur Administrateur
            user = Administrateur.objects.create(
                username=username,
                email=email,
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                genre=genre,
                date_naissance=date_naissance,
                lieu_naiss=lieu_naiss,
                fonction='ENSEIGNANT',
                is_active=True
            )
            user.set_password(password)
            user.save()

            # Déterminer le sexe
            sexe_val = "Homme" if genre == "H" else "Femme"

            # Créer l'objet Enseignant lié
            Enseignant.objects.create(
                user=user,
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                sexe=sexe_val,
                adresse=adresse,
                date_naiss=date_naissance,
                lieu_naiss=lieu_naiss,
                photo=photo,
                specialite=specialite,
                email=email,
            )

            # Enregistrer dans l’historique
            Historique.objects.create(
                user=request.user,
                action=f"A ajouté l'enseignant {prenom} {nom} ({email})"
            )

            messages.success(request, "Enseignant créé avec succès !")

        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout : {e}")

        return redirect("enseignant")

    return redirect("enseignant")
  
####################### FONCTION DE MODIFICATION DES INFORMATIONS DES ENSEIGNANTS ######################
def modifier(request, id):
    enseignant = get_object_or_404(Enseignant, id=id)
    if request.method == 'POST':
        ancien_nom = enseignant.nom
        ancien_prenom = enseignant.prenom

        # Mise à jour des champs
        enseignant.nom = request.POST.get('nom')
        enseignant.prenom = request.POST.get('prenom')
        enseignant.telephone = request.POST.get('telephone')
        enseignant.date_naiss = request.POST.get('date_naiss')

        enseignant.sexe = request.POST.get('sexe')  # <-- correct
        enseignant.adresse = request.POST.get('adresse')
        # enseignant.date_naiss = request.POST.get('naissance')
        enseignant.lieu_naiss = request.POST.get('lieu_naiss')

        enseignant.email = request.POST.get('email')
        if request.FILES.get('photo'):
            enseignant.photo = request.FILES.get('photo')

        enseignant.save()

        # ✅ Ajouter l'action dans l'historique
        Historique.objects.create(
            user=request.user,
            action=f"A modifié l'enseignant {ancien_prenom} {ancien_nom} → {enseignant.prenom} {enseignant.nom}"
        )

        messages.success(request, f"L'enseignant {enseignant.prenom} {enseignant.nom} a été modifié avec succès.")
        return redirect('enseignant')

    return render(request, 'enseignant/enseignant.html', {'enseignant': enseignant})

################## FONCTION DE SUPPRESSION DES INFORMATIONS DES ENSEIGNANTS #####################

def supprim(request, pk):
    enseignant = get_object_or_404(Enseignant, id=pk)

    # ✅ Enregistrer l’action dans l’historique avant suppression
    Historique.objects.create(
        user=request.user,
        action=f"A supprimé l'enseignant {enseignant.prenom} {enseignant.nom}"
    )

    # ✅ Supprimer l’enseignant
    enseignant.delete()

    messages.success(request, f"L'enseignant {enseignant.prenom} {enseignant.nom} a été supprimé avec succès.")
    return redirect('enseignant')


    return redirect('enseignant')
######################### DETAIL DES ENSEIGNANTS #################################
def detail_enseignant(request, id):
    enseignant = get_object_or_404(Enseignant, id=id)
    return render(request, 'enseignant/detail_enseignant.html', {'enseignant': enseignant}) 

######################### FONCTION DE PAIEMENT DES SALAIRES DES ENSEIGNANTS #################################
def calculer_solde(annee_scolaire):
    total_entre = FraisScolarite.objects.filter(
        annee_scolaire=annee_scolaire
    ).aggregate(total=Sum('total_paye'))['total'] or 0

    total_sorties_salaire = PaiementSalaire.objects.filter(
        annee_scolaire=annee_scolaire
    ).aggregate(total=Sum('montant'))['total'] or 0

    total_sorties_depense = Depense.objects.filter(
        annee_scolaire=annee_scolaire
    ).aggregate(total=Sum('montant'))['total'] or 0

    total_sorties = total_sorties_salaire + total_sorties_depense
    solde_net = total_entre - total_sorties

    return solde_net


def paiement_salaire(request):
    enseignants = Enseignant.objects.all()
    paiements = PaiementSalaire.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    if request.method == 'POST':
        enseignant_id = request.POST.get('enseignant')
        montant = request.POST.get('montant')
        date_paiement = request.POST.get('date_paiement')
        statut = request.POST.get('statut')
        annee_scolaire_id = request.POST.get('annee_scolaire')

        if enseignant_id and montant and date_paiement and annee_scolaire_id:
            try:
                montant = float(montant)
            except ValueError:
                messages.error(request, "Le montant est invalide.")
                return redirect('paiement_salaire')

            enseignant = get_object_or_404(Enseignant, id=enseignant_id)
            annee_scolaire = get_object_or_404(AnneeScolaire, id=annee_scolaire_id)

            solde = calculer_solde(annee_scolaire)

            if montant > solde:
                messages.error(request, "Le solde est insuffisant pour effectuer ce paiement.")
                return redirect('paiement_salaire')

            paiement = PaiementSalaire.objects.create(
                enseignant=enseignant,
                montant=montant,
                date_paiement=date_paiement,
                statut=statut,
                annee_scolaire=annee_scolaire,
            )

            # ✅ Historique du paiement enregistré
            Historique.objects.create(
                user=request.user,
                action=f"A payé {montant} GNF à l'enseignant {enseignant.prenom} {enseignant.nom} "
                       f"({statut}) pour l'année {annee_scolaire.nom}"
            )

            messages.success(request, "Paiement effectué avec succès.")
            return redirect('paiement_salaire')
        else:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")

    return render(request, 'enseignant/paiement_salaire.html', {
        'enseignants': enseignants,
        'paiements': paiements,
        'annees_scolaires': annees_scolaires,
    })


def supprimer_paiement(request):
    paiement_id = request.POST.get('paiement_id')
    paiement = get_object_or_404(PaiementSalaire, id=paiement_id)

    # ✅ Historique avant suppression
    Historique.objects.create(
        user=request.user,
        action=f"Suppression du paiement {paiement.montant} FCFA "
               f"({paiement.statut}) de {paiement.enseignant.prenom} {paiement.enseignant.nom} "
               f"pour l'année {paiement.annee_scolaire.nom}"
    )

    paiement.delete()
    messages.success(request, "Le paiement a été supprimé avec succès.")
    return redirect('paiement_salaire')
 
 
##############FONCTION DE MODIFICATION DES PAIEMENTS#############
def modifier_paiement(request):
    paiement_id = request.POST.get("paiement_id")
    paiement = get_object_or_404(PaiementSalaire, id=paiement_id)

    try:
        paiement.enseignant = Enseignant.objects.get(id=request.POST.get("enseignant"))
        paiement.montant = request.POST.get("montant")
        paiement.date_paiement = request.POST.get("date_paiement")
        paiement.statut = request.POST.get("statut")
        paiement.annee_scolaire = AnneeScolaire.objects.get(id=request.POST.get("annee_scolaire"))
        paiement.save()

        Historique.objects.create(
            user=request.user,
            action=f"A modifié le paiement de {paiement.montant} GNF "
                f"pour l'enseignant {paiement.enseignant.prenom} {paiement.enseignant.nom} "
                f"({paiement.statut}) pour l'année {paiement.annee_scolaire.nom} "
                f"à la date {paiement.date_paiement}"
        )
        messages.success(request, "Le paiement a été modifié avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la modification : {str(e)}")

    return redirect('paiement_salaire')


################ FONCTION D'AJOUT DES DEPENSES#############################
def ajouter_depense(request):
    annees_scolaires = AnneeScolaire.objects.all()
    depenses = Depense.objects.all()

    if request.method == 'POST':
        montant = request.POST.get('montant')
        description = request.POST.get('description')
        annee_scolaire_id = request.POST.get('annee_scolaire')

        if montant and description and annee_scolaire_id:
            try:
                montant = float(montant)
            except ValueError:
                messages.error(request, "Le montant est invalide.")
                return redirect('depense')

            annee_scolaire = get_object_or_404(AnneeScolaire, id=annee_scolaire_id)
            solde = calculer_solde(annee_scolaire)

            if montant > solde:
                messages.error(request, "Le solde est insuffisant pour effectuer cette dépense.")
                return redirect('depense')

            Depense.objects.create(
                montant=montant,
                description=description,
                annee_scolaire=annee_scolaire,
            )

            Historique.objects.create(
                user=request.user,
                action=f"A ajouté une dépense de {montant} GNF "
                    f"pour l'année {annee_scolaire.nom} "
                    f"avec la description : {description}"
            )


            messages.success(request, "Dépense enregistrée avec succès.")
            return redirect('depense')
        else:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")

    return render(request, 'enseignant/depense.html', {
        'annees_scolaires': annees_scolaires,
        'depenses': depenses,
    })

def modifier_depense(request):
    if request.method == 'POST' and request.POST.get('action') == 'modifier':
        depense_id = request.POST.get('depense_id')
        depense = get_object_or_404(Depense, id=depense_id)

        # Récupération des champs du formulaire
        description = request.POST.get('description')
        montant = request.POST.get('montant')
        date_depense = request.POST.get('date_depense')
        annee_id = request.POST.get('annee_scolaire')

        # Mise à jour des données
        depense.description = description
        depense.montant = montant
        depense.date_depense = date_depense
        depense.annee_scolaire_id = annee_id
        depense.save()

        # Ajouter dans l'historique sans année scolaire
        Historique.objects.create(
            user=request.user,
            action=f"A modifié une dépense de {montant} GNF avec la description : {description}"
        )
        messages.success(request, "Dépense modifiée avec succès.")
        return redirect('depense')  # Remplace par le nom exact de ta vue d'affichage des dépenses

    messages.error(request, "Une erreur est survenue lors de la modification.")
    return redirect('depense')

def supprimer_depense(request):
    if request.method == 'POST' and request.POST.get('action') == 'supprimer':
        depense_id = request.POST.get('depense_id')
        depense = get_object_or_404(Depense, id=depense_id)

        # Historique avant suppression
        Historique.objects.create(
            user=request.user,
            action=f"A supprimé une dépense de {depense.montant} GNF avec la description : {depense.description}"
        )

        depense.delete()
        messages.success(request, "Dépense supprimée avec succès.")
        return redirect('depense')

    messages.error(request, "Échec de la suppression.")
    return redirect('depense')



##############################LE BILAN FINANCIER ###################################
from django.db.models import Sum, F
def bilan_financier(request):
    annees_scolaires = AnneeScolaire.objects.all().order_by('-id')
    total_entrées = 0
    total_sorties = 0
    solde = 0
    total_impayes=0
    annee_scolaire = None
    selected_annee_id = request.GET.get('annee_scolaire')

    if selected_annee_id:
        try:
            annee_scolaire = AnneeScolaire.objects.get(id=selected_annee_id)

            total_entrées = FraisScolarite.objects.filter(annee_scolaire=annee_scolaire)\
                .aggregate(total=Sum('total_paye'))['total'] or 0

            total_sorties_salaire = PaiementSalaire.objects.filter(annee_scolaire=annee_scolaire)\
                .aggregate(total=Sum('montant'))['total'] or 0

            total_sorties_depense = Depense.objects.filter(annee_scolaire=annee_scolaire)\
                .aggregate(total=Sum('montant'))['total'] or 0

            total_sorties = total_sorties_salaire + total_sorties_depense
            solde = total_entrées - total_sorties

                        # Total impayé réel
            total_impayes = FraisScolarite.objects.filter(annee_scolaire=annee_scolaire)\
                .aggregate(total=Sum(F('montant_total') - F('total_paye')))['total'] or 0


            if solde <= 0:
                messages.warning(request, "Le solde est insuffisant, veuillez alimenter la caisse.")

        except AnneeScolaire.DoesNotExist:
            messages.error(request, "L'année scolaire sélectionnée n'existe pas.")
            annee_scolaire = None

    context = {
        'total_impayes':total_impayes,
        'annees_scolaires': annees_scolaires,
        'selected_annee_id': selected_annee_id,
        'total_entrées': total_entrées,
        'total_sorties': total_sorties,
        'solde': solde,
        'annee_scolaire': annee_scolaire,
    }

    return render(request, 'enseignant/bilan_financier.html', context)

############################################################################
def profi(request):

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

        return redirect("profi")
    
    context = {
        "user": user,
    }
    return render(request,'enseignant/profil.html',context)


############################################################################
def profil_comptable(request):

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
    
    context = {
        "user": user,
    }
    return render(request,'eleve/profil.html',context)



from django.shortcuts import render, redirect
from django.contrib import messages
from matiere.models import  EnseignantMatiere
from matiere.models import Matiere
from niveau.models import Niveau
from groupe_classe.models import GroupeClasse
from enseignant.models import Enseignant


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt  # si nécessaire pour AJAX (sinon configure le token CSRF dans JS)
def ajouter_affectation_ajax(request):
    if request.method == "POST":
        enseignant_id = request.POST.get('enseignant')
        niveau_id = request.POST.get('niveau')
        groupe_classe_id = request.POST.get('classe')
        matiere_id = request.POST.get('matiere')

        try:
            enseignant = Enseignant.objects.get(id=enseignant_id)
            niveau = Niveau.objects.get(id=niveau_id)
            groupe_classe = GroupeClasse.objects.get(id=groupe_classe_id)
            matiere = Matiere.objects.get(id=matiere_id)
        except (Enseignant.DoesNotExist, Niveau.DoesNotExist, GroupeClasse.DoesNotExist, Matiere.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Données invalides.'})

        # Vérifier si l'affectation existe déjà
        if EnseignantMatiere.objects.filter(
            enseignant=enseignant,
            matiere=matiere,
            niveau=niveau,
            groupe_classe=groupe_classe
        ).exists():
            return JsonResponse({'status': 'warning', 'message': 'Cet enseignant est déjà affecté à ce niveau, classe et matière.'})
        else:
            EnseignantMatiere.objects.create(
                enseignant=enseignant,
                matiere=matiere,
                niveau=niveau,
                groupe_classe=groupe_classe
            )
            return JsonResponse({'status': 'success', 'message': 'Affectation réussie !'})
    
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'})

    

from django.http import JsonResponse


def get_classes_matiere(request):
    niveau_id = request.GET.get('niveau')
    classes = list(GroupeClasse.objects.filter(niveau_id=niveau_id).values('id', 'nom'))
    matieres = list(Matiere.objects.filter(niveau_id=niveau_id).values('id', 'nom'))
    return JsonResponse({'classes': classes, 'matieres': matieres})



#SUIVIE DES ENSEIGNANTS
def suivi(request):
    suivies=EnseignantMatiere.objects.all()
    enseignants = Enseignant.objects.all()
    niveaux = Niveau.objects.all()
    groupes = GroupeClasse.objects.all()  # ← c'est ça qui alimente ton select
    matieres = Matiere.objects.all()

    context = {
        'suivies':suivies,
        'enseignants': enseignants,
        'niveaux': niveaux,
        'groupes': groupes,
        'matieres': matieres,
    }
    return render(request, 'enseignant/suivie.html', context)

@login_required
def change_password(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('cpwd')
        auto_login = request.POST.get('connect')  # checkbox pour rester connecté

        # Vérifications côté serveur
        if not password or not confirm_password:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('change_password')

        if password != confirm_password:
            messages.error(request, "Les mots de passe ne sont pas identiques.")
            return redirect('change_password')

        if len(password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect('change_password')
        
        if not any(char.isdigit() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins un chiffre.")
            return redirect('change_password')
        
        if not any(char.isalpha() for char in password):
            messages.error(request, "Le mot de passe doit contenir au moins une lettre.")
            return redirect('change_password')


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
            return redirect('change_password')
        else:
            logout(request)
            messages.success(request, "Mot de passe changé, veuillez vous reconnecter.")
            return redirect('login')

    return render(request, 'enseignant/change_password.html')



def historique_comptable(request):
    
    if request.user.is_superuser:
        # Super utilisateur : voir tous les historiques
        historiques = Historique.objects.all().order_by('-created_time')
    else:
        # Utilisateur normal : voir uniquement ses propres actions
        historiques = Historique.objects.filter(user=request.user).order_by('-created_time')

    return render(request, 'enseignant/historique.html', {'historiques': historiques})


###################################################################
#LES DROIT DU FONDATEUR
# #################################################################

##############################LE BILAN FINANCIER ###################################
def finance(request):
    annees_scolaires = AnneeScolaire.objects.all().order_by('-id')
    total_entrées = 0
    total_sorties = 0
    solde = 0
    annee_scolaire = None
    selected_annee_id = request.GET.get('annee_scolaire')

    if selected_annee_id:
        try:
            annee_scolaire = AnneeScolaire.objects.get(id=selected_annee_id)

            total_entrées = FraisScolarite.objects.filter(annee_scolaire=annee_scolaire)\
                .aggregate(total=Sum('total_paye'))['total'] or 0

            total_sorties_salaire = PaiementSalaire.objects.filter(annee_scolaire=annee_scolaire)\
                .aggregate(total=Sum('montant'))['total'] or 0

            total_sorties_depense = Depense.objects.filter(annee_scolaire=annee_scolaire)\
                .aggregate(total=Sum('montant'))['total'] or 0

            total_sorties = total_sorties_salaire + total_sorties_depense
            solde = total_entrées - total_sorties

            if solde <= 0:
                messages.warning(request, "Le solde est insuffisant, veuillez alimenter la caisse.")

        except AnneeScolaire.DoesNotExist:
            messages.error(request, "L'année scolaire sélectionnée n'existe pas.")
            annee_scolaire = None

    context = {
        'annees_scolaires': annees_scolaires,
        'selected_annee_id': selected_annee_id,
        'total_entrées': total_entrées,
        'total_sorties': total_sorties,
        'solde': solde,
        'annee_scolaire': annee_scolaire,
    }

    return render(request, 'admin/bilan_financier.html', context)


################ FONCTION D'AJOUT DES DEPENSES#############################
def ajouter_depense_fondateur(request):
    annees_scolaires = AnneeScolaire.objects.all()
    depenses = Depense.objects.all()

    return render(request, 'admin/depense.html', {
        'annees_scolaires': annees_scolaires,
        'depenses': depenses,
    })


# --- LISTE DES ENSEIGNANTS ---
def enseignant_fondateur(request):
    enseignants = Enseignant.objects.all()
    niveaux = Niveau.objects.all()
    groupes = GroupeClasse.objects.all()
    matieres = Matiere.objects.all()

    context = {
        'enseignants': enseignants,
        'niveaux': niveaux,
        'groupes': groupes,
        'matieres': matieres,
    }
    return render(request, 'admin/data.html', context)


######################### DETAIL DES ENSEIGNANTS #################################
def detail_enseignant_fonda(request, id):
    enseignant = get_object_or_404(Enseignant, id=id)
    return render(request, 'admin/detail_enseignant.html', {'enseignant': enseignant}) 




def paiement_salaire_fonda(request):
    enseignants = Enseignant.objects.all()
    paiements = PaiementSalaire.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    return render(request, 'admin/paiement_salaire.html', {
        'enseignants': enseignants,
        'paiements': paiements,
        'annees_scolaires': annees_scolaires,
    })

    #SUIVIE DES ENSEIGNANTS
def suivie_ensei(request):
    suivies=EnseignantMatiere.objects.all()
    enseignants = Enseignant.objects.all()
    niveaux = Niveau.objects.all()
    groupes = GroupeClasse.objects.all()  # ← c'est ça qui alimente ton select
    matieres = Matiere.objects.all()

    context = {
        'suivies':suivies,
        'enseignants': enseignants,
        'niveaux': niveaux,
        'groupes': groupes,
        'matieres': matieres,
    }
    return render(request, 'admin/suivie_enseignant.html', context)


from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from eleve.models import Eleve
from groupe_classe.models import GroupeClasse
from annee_scolaire.models import AnneeScolaire
from bulletin.models import BulletinTrimestriel
from cycle.models import Etablissement

# from enseignant.models import EnseignantMatiere


# ============================================================
# GROUPES AUTORISÉS POUR L'ENSEIGNANT
# ============================================================

def groupes_autorises_enseignant(enseignant):

    return (
        GroupeClasse.objects
        .filter(
            id__in=(
                EnseignantMatiere.objects
                .filter(
                    enseignant=enseignant
                )
                .values_list(
                    'groupe_classe_id',
                    flat=True
                )
            )
        )
        .distinct()
    )


# ============================================================
# RÉSULTAT TRIMESTRIEL D'UNE CLASSE
# ADAPTÉ À EleveInscrit
# ============================================================

@login_required
def resultat_trimestriel_classe(request):

    # ========================================================
    # VÉRIFIER L'ENSEIGNANT
    # ========================================================

    enseignant = getattr(
        request.user,
        'enseignant_profile',
        None
    )

    if not enseignant:

        messages.error(
            request,
            "Accès réservé aux enseignants."
        )

        return redirect('login')


    # ========================================================
    # DONNÉES GÉNÉRALES
    # ========================================================

    ecoles = Etablissement.objects.all()

    annees_scolaires = (
        AnneeScolaire.objects.all()
    )


    # ========================================================
    # GROUPES AUTORISÉS
    # ========================================================

    groupes_classes = (
        groupes_autorises_enseignant(
            enseignant
        )
    )


    # ========================================================
    # PARAMÈTRES
    # ========================================================

    groupe_id = request.GET.get(
        'groupe_classe'
    )

    annee_id = request.GET.get(
        'annee_scolaire'
    )

    trimestre_param = request.GET.get(
        'trimestre'
    )


    # ========================================================
    # VARIABLES
    # ========================================================

    bulletins_list = []

    groupe_obj = None

    annee_scolaire_obj = None

    trimestre = None

    trimestre_label = ""


    # ========================================================
    # STATISTIQUES
    # ========================================================

    statistiques = {

        'total_inscrits': 0,

        'ayant_composes': 0,

        'admis': 0,

        'non_admis': 0,

        'filles_total': 0,

        'filles_composes': 0,

        'filles_admis': 0,

        'filles_non_admis': 0,

        'taux_reussite': 0,

        'taux_filles_reussite': 0,

    }


    # ========================================================
    # FILTRAGE
    # ========================================================

    if (
        groupe_id
        and annee_id
        and trimestre_param
    ):

        try:

            # ==================================================
            # VÉRIFIER LE GROUPE AUTORISÉ
            # ==================================================

            groupe_obj = (
                groupes_classes.get(
                    id=groupe_id
                )
            )


            # ==================================================
            # ANNÉE SCOLAIRE
            # ==================================================

            annee_scolaire_obj = (
                AnneeScolaire.objects.get(
                    id=annee_id
                )
            )


            # ==================================================
            # TRIMESTRE
            # ==================================================

            trimestre = int(
                trimestre_param
            )


            if trimestre not in [1, 2, 3]:

                raise ValueError(
                    "Trimestre invalide"
                )


            trimestre_label = (
                f"Trimestre {trimestre}"
            )


        except (
            GroupeClasse.DoesNotExist,
            AnneeScolaire.DoesNotExist,
            ValueError,
            TypeError
        ):

            messages.error(
                request,
                "Classe, année scolaire ou trimestre invalide."
            )

            return render(
                request,
                "enseignant/resultat_trimestriel_classe.html",
                {
                    'groupes_classes':
                        groupes_classes,

                    'annees_scolaires':
                        annees_scolaires,

                    'sorted_bulletins':
                        [],

                    'statistiques':
                        statistiques,

                    'ecoles':
                        ecoles,
                }
            )


        # ====================================================
        # INSCRIPTIONS DES ÉLÈVES
        # ====================================================
        #
        # IMPORTANT :
        # On utilise EleveInscrit.
        #
        # Cela permet de récupérer uniquement les élèves
        # réellement inscrits dans cette classe pour
        # l'année scolaire sélectionnée.
        #
        # ====================================================

        inscriptions = (
            EleveInscrit.objects
            .filter(
                groupe_classe=groupe_obj,
                annee_scolaire=annee_scolaire_obj
            )
            .select_related(
                'eleve',
                'groupe_classe',
                'groupe_classe__niveau',
                'groupe_classe__niveau__cycle'
            )
        )


        # ====================================================
        # IDENTIFIANTS DES ÉLÈVES INSCRITS
        # ====================================================

        eleves_ids = inscriptions.values_list(
            'eleve_id',
            flat=True
        )


        # ====================================================
        # BULLETINS DU TRIMESTRE
        # ====================================================

        bulletins = (
            BulletinTrimestriel.objects
            .filter(
                eleve_id__in=eleves_ids,
                annee_scolaire=annee_scolaire_obj,
                trimestre=trimestre
            )
            .select_related(
                'eleve'
            )
        )


        # ====================================================
        # DICTIONNAIRE DES INSCRIPTIONS
        # ====================================================

        inscriptions_dict = {

            inscription.eleve_id:
                inscription

            for inscription in inscriptions

        }


        # ====================================================
        # SEUIL D'ADMISSION
        # ====================================================

        cycle_nom = ""

        if (
            groupe_obj.niveau
            and groupe_obj.niveau.cycle
        ):

            cycle_nom = (
                groupe_obj
                .niveau
                .cycle
                .nom
                .strip()
                .lower()
            )


        if cycle_nom == "primaire":

            seuil = 5

        else:

            seuil = 10


        # ====================================================
        # PRÉPARER LES BULLETINS
        # ====================================================

        for bulletin in bulletins:

            moyenne = (
                bulletin.moyenne_totale
                or 0
            )


            # ==================================================
            # INSCRIPTION
            # ==================================================

            inscription = (
                inscriptions_dict.get(
                    bulletin.eleve_id
                )
            )


            # ==================================================
            # AJOUT
            # ==================================================

            bulletins_list.append({

                'bulletin':
                    bulletin,

                'inscription':
                    inscription,

                'eleve':
                    bulletin.eleve,

                'moyenne':
                    round(
                        float(moyenne),
                        2
                    ),

                'observation':
                    bulletin.observation
                    or "-",

            })


        # ====================================================
        # CLASSEMENT
        # ====================================================

        bulletins_list.sort(

            key=lambda x: (
                x['moyenne']
                if x['moyenne'] is not None
                else 0
            ),

            reverse=True
        )


        # ====================================================
        # ATTRIBUTION DES RANGS
        # ====================================================

        rang = 0

        previous_moyenne = None


        for index, item in enumerate(
            bulletins_list,
            start=1
        ):

            moyenne = item['moyenne']


            # =================================================
            # EX ÆQUO
            # =================================================

            if (
                previous_moyenne is not None
                and moyenne == previous_moyenne
            ):

                item['rang'] = (
                    f"{rang} Ex"
                )


            # =================================================
            # NOUVEAU RANG
            # =================================================

            else:

                rang = index

                if rang == 1:

                    item['rang'] = "1er"

                else:

                    item['rang'] = (
                        f"{rang}ème"
                    )


            previous_moyenne = moyenne


        # ====================================================
        # STATISTIQUES
        # ====================================================

        # Nombre réel d'élèves inscrits dans la classe
        statistiques[
            'total_inscrits'
        ] = inscriptions.count()


        # ====================================================
        # ÉLÈVES AYANT COMPOSÉ
        # ====================================================

        bulletins_avec_notes = [

            item

            for item in bulletins_list

            if item['moyenne'] > 0

        ]


        statistiques[
            'ayant_composes'
        ] = len(
            bulletins_avec_notes
        )


        # ====================================================
        # ADMIS
        # ====================================================

        statistiques[
            'admis'
        ] = len([

            item

            for item in bulletins_avec_notes

            if item['moyenne'] >= seuil

        ])


        # ====================================================
        # NON ADMIS
        # ====================================================

        statistiques[
            'non_admis'
        ] = (

            statistiques[
                'ayant_composes'
            ]

            -

            statistiques[
                'admis'
            ]

        )


        # ====================================================
        # TAUX DE RÉUSSITE
        # ====================================================

        if statistiques[
            'ayant_composes'
        ] > 0:

            statistiques[
                'taux_reussite'
            ] = round(

                (
                    statistiques['admis']
                    /
                    statistiques['ayant_composes']
                )
                * 100,

                2

            )


        # ====================================================
        # FILLES INSCRITES
        # ====================================================

        filles = [

            inscription

            for inscription in inscriptions

            if (
                inscription.eleve.genre
                and
                inscription.eleve.genre
                .strip()
                .lower()
                == "femme"
            )

        ]


        statistiques[
            'filles_total'
        ] = len(filles)


        # ====================================================
        # FILLES AYANT COMPOSÉ
        # ====================================================

        filles_composes = [

            item

            for item in bulletins_avec_notes

            if (
                item['eleve'].genre
                and
                item['eleve'].genre
                .strip()
                .lower()
                == "femme"
            )

        ]


        statistiques[
            'filles_composes'
        ] = len(
            filles_composes
        )


        # ====================================================
        # FILLES ADMISES
        # ====================================================

        statistiques[
            'filles_admis'
        ] = len([

            item

            for item in filles_composes

            if item['moyenne'] >= seuil

        ])


        # ====================================================
        # FILLES NON ADMISES
        # ====================================================

        statistiques[
            'filles_non_admis'
        ] = (

            statistiques[
                'filles_composes'
            ]

            -

            statistiques[
                'filles_admis'
            ]

        )


        # ====================================================
        # TAUX DE RÉUSSITE DES FILLES
        # ====================================================

        if statistiques[
            'filles_composes'
        ] > 0:

            statistiques[
                'taux_filles_reussite'
            ] = round(

                (
                    statistiques[
                        'filles_admis'
                    ]
                    /
                    statistiques[
                        'filles_composes'
                    ]
                )
                * 100,

                2

            )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        'groupes_classes':
            groupes_classes,

        'annees_scolaires':
            annees_scolaires,

        'sorted_bulletins':
            bulletins_list,

        'groupe_obj':
            groupe_obj,

        'annee_scolaire_obj':
            annee_scolaire_obj,

        'trimestre':
            trimestre,

        'trimestre_label':
            trimestre_label,

        'statistiques':
            statistiques,

        'ecoles':
            ecoles,

        'groupe_id':
            groupe_id,

        'annee_scolaire_id':
            annee_id,

    }


    # ========================================================
    # AFFICHAGE
    # ========================================================

    return render(
        request,
        "enseignant/resultat_trimestriel_classe.html",
        context
    )







@login_required



# ============================================================
# BULLETIN TRIMESTRIEL ENSEIGNANT
# ADAPTÉ À EleveInscrit
# ============================================================

def bulletin_trimestriel_enseignant(request):

    # ========================================================
    # ENSEIGNANT CONNECTÉ
    # ========================================================

    enseignant = getattr(
        request.user,
        'enseignant_profile',
        None
    )

    if not enseignant:
        messages.error(
            request,
            "Accès refusé."
        )
        return redirect('home')


    # ========================================================
    # CLASSES AUTORISÉES POUR L'ENSEIGNANT
    # ========================================================

    groupes_classes = groupes_autorises_enseignant(
        enseignant
    )


    # ========================================================
    # DONNÉES POUR LES FILTRES
    # ========================================================

    annees_scolaires = AnneeScolaire.objects.all()

    ecoles = Etablissement.objects.all()

    bulletins_trimestriels = []


    # ========================================================
    # PARAMÈTRES
    # ========================================================

    groupe_id = request.GET.get(
        'groupe_classe'
    )

    annee_id = request.GET.get(
        'annee_scolaire'
    )

    trimestre = request.GET.get(
        'trimestre'
    )


    # ========================================================
    # SÉCURITÉ
    # ========================================================

    if groupe_id:

        if not groupes_classes.filter(
            id=groupe_id
        ).exists():

            messages.error(
                request,
                "Vous n'êtes pas autorisé à accéder à cette classe."
            )

            return redirect(request.path)


    # ========================================================
    # TRAITEMENT
    # ========================================================

    if (
        groupe_id
        and annee_id
        and trimestre
    ):

        # ====================================================
        # RÉCUPÉRER LES INSCRIPTIONS
        # ====================================================

        inscriptions = (
            EleveInscrit.objects
            .filter(
                groupe_classe_id=groupe_id,
                annee_scolaire_id=annee_id,
                actif=True,
                eleve__actif=True
            )
            .select_related(
                'eleve',
                'groupe_classe',
                'groupe_classe__niveau',
                'niveau',
                'niveau__cycle',
                'annee_scolaire'
            )
        )


        # ====================================================
        # TRAITER CHAQUE INSCRIPTION
        # ====================================================

        for inscription in inscriptions:

            eleve = inscription.eleve


            # =================================================
            # NOTES DE L'ÉLÈVE
            # =================================================

            notes = (
                Note.objects
                .filter(
                    inscription=inscription,
                    trimestre=trimestre,
                    annee_scolaire_id=annee_id
                )
                .values(
                    'matiere__nom'
                )
                .annotate(
                    moyenne_matiere=Avg(
                        'note_finale'
                    )
                )
                .order_by(
                    'matiere__nom'
                )
            )


            # =================================================
            # MOYENNE GÉNÉRALE
            # =================================================

            moyenne_totale = notes.aggregate(
                m=Avg(
                    'moyenne_matiere'
                )
            )['m']


            if moyenne_totale is not None:

                moyenne_totale = round(
                    float(moyenne_totale),
                    2
                )


            # =================================================
            # BULLETIN TRIMESTRIEL
            # =================================================

            bulletin = (
                BulletinTrimestriel.objects
                .filter(
                    eleve=eleve,
                    trimestre=trimestre,
                    annee_scolaire_id=annee_id
                )
                .first()
            )


            # =================================================
            # MOYENNE DU BULLETIN
            # =================================================

            if bulletin is not None:

                moyenne_bulletin = (
                    bulletin.moyenne_totale
                )

            else:

                moyenne_bulletin = (
                    moyenne_totale
                )


            # =================================================
            # OBSERVATION
            # =================================================

            observation = "-"

            if moyenne_bulletin is not None:

                # ------------------------------------------------
                # RÉCUPÉRER LE CYCLE DE L'INSCRIPTION
                # ------------------------------------------------

                cycle_nom = ""

                if inscription.niveau:

                    if inscription.niveau.cycle:

                        cycle_nom = (
                            inscription
                            .niveau
                            .cycle
                            .nom
                            .strip()
                            .lower()
                        )

                # ------------------------------------------------
                # PRIMAIRE
                # ------------------------------------------------

                if cycle_nom == "primaire":

                    if moyenne_bulletin == 10:

                        observation = "Excellent"

                    elif moyenne_bulletin >= 8:

                        observation = "Très Bien"

                    elif moyenne_bulletin >= 7:

                        observation = "Bien"

                    elif moyenne_bulletin >= 6:

                        observation = "Assez Bien"

                    elif moyenne_bulletin >= 5:

                        observation = "Passable"

                    else:

                        observation = "Faible"


                # ------------------------------------------------
                # COLLÈGE / LYCÉE / AUTRE
                # ------------------------------------------------

                else:

                    if moyenne_bulletin == 20:

                        observation = "Excellent"

                    elif moyenne_bulletin >= 16:

                        observation = "Très Bien"

                    elif moyenne_bulletin >= 14:

                        observation = "Bien"

                    elif moyenne_bulletin >= 12:

                        observation = "Assez Bien"

                    elif moyenne_bulletin >= 10:

                        observation = "Passable"

                    else:

                        observation = "Faible"


            # =================================================
            # RANG
            # =================================================

            rang_formate = "-"

            if moyenne_bulletin is not None:

                # Le rang sera recalculé plus bas
                # pour toute la classe.

                if bulletin is not None:

                    try:

                        ancien_rang = bulletin.get_rang()

                        if ancien_rang:

                            rang_formate = ancien_rang

                    except Exception:

                        rang_formate = "-"


            # =================================================
            # AJOUT DU BULLETIN
            # =================================================

            bulletins_trimestriels.append({

                'bulletin':
                    bulletin,

                'inscription':
                    inscription,

                'eleve':
                    eleve,

                'notes':
                    notes,

                'moyenne_totale':
                    moyenne_bulletin,

                'rang_formate':
                    rang_formate,

                'observation':
                    observation,

            })


    # ========================================================
    # CLASSEMENT PAR MOYENNE
    # ========================================================

    bulletins_trimestriels.sort(
        key=lambda x: (
            x['moyenne_totale']
            if x['moyenne_totale'] is not None
            else 0
        ),
        reverse=True
    )


    # ========================================================
    # CALCUL DES RANGS
    # ========================================================

    rang = 0

    previous_moyenne = None


    for index, item in enumerate(
        bulletins_trimestriels,
        start=1
    ):

        moyenne = item['moyenne_totale']


        # ====================================================
        # PAS DE MOYENNE
        # ====================================================

        if moyenne is None:

            item['rang_formate'] = "-"

            continue


        # ====================================================
        # EX ÆQUO
        # ====================================================

        if (
            previous_moyenne is not None
            and moyenne == previous_moyenne
        ):

            item['rang_formate'] = (
                f"{rang}e Ex"
            )


        # ====================================================
        # NOUVEAU RANG
        # ====================================================

        else:

            rang = index

            if rang == 1:

                item['rang_formate'] = "1er"

            else:

                item['rang_formate'] = (
                    f"{rang}ème"
                )


        previous_moyenne = moyenne


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        'groupes_classes':
            groupes_classes,

        'annees_scolaires':
            annees_scolaires,

        'bulletins_trimestriels':
            bulletins_trimestriels,

        'ecoles':
            ecoles,

        'groupe_id':
            groupe_id,

        'annee_scolaire_id':
            annee_id,

        'trimestre':
            trimestre,

    }


    # ========================================================
    # AFFICHAGE
    # ========================================================

    return render(
        request,
        'enseignant/bulletin_trimestriel_classe.html',
        context
    )

from django.db.models import Q
@login_required
def gestion_badges_enseignants(request):

    recherche = request.GET.get(
        'recherche',
        ''
    ).strip()

    enseignants = Enseignant.objects.all()

    if recherche:

        enseignants = enseignants.filter(
            Q(nom__icontains=recherche)
            |
            Q(prenom__icontains=recherche)
            |
            Q(specialite__icontains=recherche)
            |
            Q(telephone__icontains=recherche)
            |
            Q(email__icontains=recherche)
        )

    enseignants = enseignants.order_by(
        'nom',
        'prenom'
    )

    etablissement = (
        Etablissement.objects
        .first()
    )

    context = {
        'enseignants': enseignants,
        'etablissement': etablissement,
        'recherche': recherche,
    }

    return render(
        request,
        'enseignant/gestion_badges_enseignants.html',
        context
    )


@login_required
def badge_enseignant(request, enseignant_id):

    enseignant = get_object_or_404(
        Enseignant.objects.select_related('user'),
        id=enseignant_id
    )

    etablissement = (
        Etablissement.objects
        .first()
    )

    context = {
        'enseignant': enseignant,
        'etablissement': etablissement,
    }

    return render(
        request,
        'enseignant/badge_enseignant.html',
        context
    )


@login_required
def badges_enseignants_impression(request):

    if request.method != 'POST':
        return redirect('gestion_badges_enseignants')

    enseignants_ids = request.POST.getlist('enseignants')

    enseignants_ids = [
        identifiant
        for identifiant in enseignants_ids
        if identifiant
    ]

    if not enseignants_ids:
        messages.warning(
            request,
            "Veuillez sélectionner au moins un enseignant."
        )
        return redirect('gestion_badges_enseignants')

    enseignants = (
        Enseignant.objects
        .filter(id__in=enseignants_ids)
        .select_related('user')
        .order_by('nom', 'prenom')
    )

    if not enseignants.exists():
        messages.error(
            request,
            "Aucun enseignant correspondant."
        )
        return redirect('gestion_badges_enseignants')

    etablissement = Etablissement.objects.first()

    context = {
        'enseignants': enseignants,
        'etablissement': etablissement,
        'nombre_enseignants': enseignants.count(),
    }

    return render(
        request,
        'enseignant/impression_badges_enseignants.html',
        context
    )
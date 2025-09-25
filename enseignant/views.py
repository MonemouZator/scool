from django.shortcuts import render,redirect,get_object_or_404
from enseignant.models import Enseignant,PaiementSalaire
from django.shortcuts import render, redirect
from .models import Depense
from django.contrib import messages
from eleve .models import Eleve , FraisScolarite
from annee_scolaire.models import AnneeScolaire
from personnel.models import Administrateur
from django.db.models import Sum
from django.db import models  # Importation de models
from datetime import datetime
from matiere.models import EnseignantMatiere
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

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


from personnel.models import Historique, Administrateur

# --- AJOUT D'UN ENSEIGNANT ---


# --- AJOUT D'UN ENSEIGNANT ---
def ajout_enseignant(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        telephone = request.POST.get("telephone")
        genre = request.POST.get("genre")
        date_naissance = request.POST.get("date_naissance")
        lieu_naiss = request.POST.get("lieu_naiss")
        specialite = request.POST.get("specialite")
        adresse = request.POST.get("adresse")
        photo = request.FILES.get("photo")

        # ✅ Vérification date
        try:
            date_naissance = datetime.strptime(date_naissance, "%Y-%m-%d").date()
        except Exception:
            messages.error(request, "Date de naissance invalide.")
            return redirect("enseignant")

        try:
            # ✅ Créer l'utilisateur Administrateur
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

            # ✅ Déterminer le sexe
            sexe_val = "Homme" if genre == "H" else "Femme"

            # ✅ Créer l'objet Enseignant lié
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

            # ✅ Enregistrer dans l’historique
            Historique.objects.create(
                user=request.user,
                action=f"A ajouté l'enseignant {prenom} {nom} ({email})"
            )

            messages.success(request, "Enseignant créé avec succès !")

        except IntegrityError:
            messages.error(request, "Nom d’utilisateur ou email déjà utilisé.")
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

        if len(password) < 6:
            messages.error(request, "Le mot de passe doit contenir au moins 6 caractères.")
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
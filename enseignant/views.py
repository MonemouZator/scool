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

##################### LISTE DES ENSEIGNANTS ###################################

def maitre(request):
        
        enseignants=Enseignant.objects.all()
        context={
            'enseignants':enseignants
        }
        return render(request, 'base/pages/tables/data.html',context)

################## FONCTION D'ENREGISTREMENT DES ENSEIGNANTS ####################

def ajout(request):
    if request.method=="POST": 
           
            nom=request.POST.get('nom')
            prenom=request.POST.get('prenom')
            tel=request.POST.get('tel')
            sexe=request.POST.get('sexe')
            adresse=request.POST.get('adresse')
            date=request.POST.get('naissance')
            lieu=request.POST.get('lieu')
            photo=request.POST.get('photo')
            specilite=request.POST.get('sp')
            email=request.POST.get('email')
            ensi=Enseignant.objects.create(
                nom=nom,
                prenom=prenom,
                telephone=tel,
                Sexe=sexe,
                adresse=adresse,
                date_naiss=date,
                lieu_naiss=lieu,
                photo=photo,
                specialite=specilite,
                email=email,
            )
            ensi.save()

            return redirect('enseignant')
    else:
        return redirect('enseignant')
  
####################### FONCTION DE MODIFICATION DES INFORMATIONS DES ENSEIGNANRS ######################
def modifier(request, id):
    enseignant = get_object_or_404(Enseignant, id=id)
    if request.method == 'POST':
        enseignant.nom = request.POST.get('nom')
        enseignant.prenom = request.POST.get('prenom')
        enseignant.telephone = request.POST.get('tel')
        enseignant.Sexe  = request.POST.get('sexe')
        enseignant.adresse = request.POST.get('adresse')
        enseignant.date_naiss = request.POST.get('naissance')
        enseignant.lieu_naiss = request.POST.get('lieu')
        enseignant.email = request.POST.get('email')
        if request.FILES.get('photo'):
            enseignant.photo = request.FILES.get('photo')
        enseignant.save()
        return redirect('enseignant')  # Rediriger après la mise à jour
    return render(request, 'enseignant/enseignant.html', {'enseignant': enseignant})
        
################## FONCTION DE SUPPRESSION DES INFORMATIONS DES ENSEIGNANTS #####################

def  supprim(request,pk):
    enseignant=get_object_or_404(Enseignant,id=pk)
    enseignant.delete()

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

            PaiementSalaire.objects.create(
                enseignant=enseignant,
                montant=montant,
                date_paiement=date_paiement,
                statut=statut,
                annee_scolaire=annee_scolaire,
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
    
    paiement.delete()
    messages.success(request, "Le paiement a été supprimé avec succès.")
    
    # Redirige vers la page où se trouve la liste des paiements
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

        messages.success(request, "Dépense modifiée avec succès.")
        return redirect('depense')  # Remplace par le nom exact de ta vue d'affichage des dépenses

    messages.error(request, "Une erreur est survenue lors de la modification.")
    return redirect('depense')

def supprimer_depense(request):
    if request.method == 'POST' and request.POST.get('action') == 'supprimer':
        depense_id = request.POST.get('depense_id')
        depense = get_object_or_404(Depense, id=depense_id)

        depense.delete()
        messages.success(request, "Dépense supprimée avec succès.")
        return redirect('depense')  # Remplace par le nom de ta vue principale

    messages.error(request, "Échec de la suppression.")
    return redirect('depense')


##############################LE BILAN FINANCIER ###################################
def bilan_financier(request):
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



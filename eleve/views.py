from django.shortcuts import render
from django.shortcuts import render,redirect,get_object_or_404
from niveau.models import Niveau
from groupe_classe.models import GroupeClasse
from annee_scolaire.models import AnneeScolaire
from eleve.models import Eleve,Recu,FraisScolarite
from django.core.exceptions import ValidationError
from datetime import date
from datetime import datetime,timezone
from decimal import Decimal
from django.contrib import messages
from personnel.models import Administrateur, Historique

# LISTE TOTALE DES ELEVES.
def liste_totale_eleve(request):
    niveaus=Niveau.objects.all()
    groupes=GroupeClasse.objects.all()
    annes=AnneeScolaire.objects.all()
    eleves=Eleve.objects.all()
    context={
                "eleves":eleves,
                "niveaus":niveaus,
                "groupes":groupes,
                "annes":annes,
        }
    return render(request,'eleve/liste_totale_eleve.html',context)

def formeleve(request):
    niveaus=Niveau.objects.all()
    groupes=GroupeClasse.objects.all()
    annes=AnneeScolaire.objects.all()
    eleves=Eleve.objects.all()
    context={
                "eleves":eleves,
                "niveaus":niveaus,
                "groupes":groupes,
                "annes":annes,
        }

    return render(request,'eleve/ajout_eleve.html',context)

def forme_modifie(request):
    niveaus=Niveau.objects.all()
    groupes=GroupeClasse.objects.all()
    annes=AnneeScolaire.objects.all()
    eleves=Eleve.objects.all()
    context={
                "eleves":eleves,
                "niveaus":niveaus,
                "groupes":groupes,
                "annes":annes,
        }

    return render(request,'eleve/ajout_modifier.html',context)

# Fonction de validation de la date de naissance
def validate_birthdate(value):
    if value >= date.today():
        raise ValidationError("L'élève doit avoir aumoins 8 ans.")

def ajout(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        niveau_id = request.POST.get('nive')
        groupe_id = request.POST.get('group')
        annee_id = request.POST.get('anne')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        genre = request.POST.get('sexe')
        contact = request.POST.get('contact')
        photo = request.FILES.get('photo')
        naissance = request.POST.get('date')
        lieu = request.POST.get('lieu')
        pere = request.POST.get('pere')
        fonction_pere = request.POST.get('fp')
        contact_pere = request.POST.get('cp')
        mere = request.POST.get('mere')
        fonction_mere = request.POST.get('fm')
        cm = request.POST.get('cm')

        # Vérifier doublon par nom/prénom/niveau/année
        if Eleve.objects.filter(
            nom=nom,
            prenom=prenom,
            niveau_id=niveau_id,
            annee_scolaire_id=annee_id
        ).exists():
            messages.error(request, "Cet élève est déjà inscrit dans ce niveau pour l'année sélectionnée.")
            return render(request, 'eleve/ajout_eleve.html')

        # Validation de la date de naissance
        try:
            naissance_date = date.fromisoformat(naissance)
            validate_birthdate(naissance_date)
        except ValueError:
            messages.error(request, "La date de naissance est invalide.")
            return render(request, 'eleve/ajout_eleve.html')
        except ValidationError as e:
            messages.error(request, e.message)
            return render(request, 'eleve/ajout_eleve.html')

        # Récupération des objets liés
        niveau_obj = get_object_or_404(Niveau, id=niveau_id)
        groupe_obj = get_object_or_404(GroupeClasse, id=groupe_id)
        annee_obj = get_object_or_404(AnneeScolaire, id=annee_id)

        # Création de l'élève
        eleve = Eleve.objects.create(
            groupe_classe=groupe_obj,
            annee_scolaire=annee_obj,
            niveau=niveau_obj,
            nom=nom,
            prenom=prenom,
            date_naissance=naissance_date,
            genre=genre,
            telephone=contact,
            lieu_naissance=lieu,
            photo=photo,
            contact_mere=cm,
            mere=mere,
            profession_mere=fonction_mere,
            profession_pere=fonction_pere,
            pere=pere,
            contact_parent=contact_pere
        )

        # Création des frais de scolarité associés
        if not FraisScolarite.objects.filter(eleve=eleve, annee_scolaire=annee_obj).exists():
            montant_total = niveau_obj.montant_frais or 0
            tranche1 = round(montant_total / 3, 2)
            tranche2 = round(montant_total / 3, 2)
            tranche3 = montant_total - (tranche1 + tranche2)
            FraisScolarite.objects.create(
                eleve=eleve,
                annee_scolaire=annee_obj,
                montant_total=montant_total,
                tranche1=tranche1,
                tranche2=tranche2,
                tranche3=tranche3,
                total_paye=0,
                solde=montant_total,
                est_paye=False
            )
            # Après création réussie de l'élève
            Historique.objects.create(
                user=request.user,
                action=f"A ajouté l'élève {prenom} {nom} en {niveau_obj.nom} pour l'année {annee_obj.nom}"
            )


        messages.success(request, f"L'élève {prenom} {nom} a été ajouté avec succès.")
        return redirect('forme')

    return render(request, 'eleve/ajout_eleve.html')

from django.http import JsonResponse

def get_groupes(request):
    niveau_id = request.GET.get('niveau')
    groupes = list(GroupeClasse.objects.filter(niveau_id=niveau_id).values('id', 'nom'))
    return JsonResponse({'groupes': groupes})


#FONCTION DE MODIFICATION
def modifier(request, pk):
    # Récupérer l'élève à modifier
    eleve = get_object_or_404(Eleve, pk=pk)

    if request.method == 'POST':
        # Récupérer les données du formulaire
        niveau_id = request.POST.get('niveau')
        groupe_classe_id = request.POST.get('groupe_classe')
        annee_scolaire_id = request.POST.get('annee_scolaire')

        # Validation des relations avec les modèles
        try:
            niveau = get_object_or_404(Niveau, id=int(niveau_id)) if niveau_id else None
            groupe_classe = get_object_or_404(GroupeClasse, id=int(groupe_classe_id)) if groupe_classe_id else None
            annee_scolaire = get_object_or_404(AnneeScolaire, id=int(annee_scolaire_id)) if annee_scolaire_id else None
        except ValueError:
            messages.error(request, "Les valeurs des champs sont incorrectes.")
            return redirect('modifier_eleve', pk=pk)
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {str(e)}")
            return redirect('modifier_eleve', pk=pk)

        # Mettre à jour les informations de l'élève
        eleve.niveau = niveau
        eleve.groupe_classe = groupe_classe
        eleve.annee_scolaire = annee_scolaire  # ✅ Correctement assigné
        eleve.nom = request.POST.get('nom')
        eleve.prenom = request.POST.get('prenom')
        eleve.date_naissance = request.POST.get('date_naissance')
        eleve.lieu_naissance = request.POST.get('lieu_naissance')
        eleve.genre = request.POST.get('genre')
        eleve.telephone = request.POST.get('telephone')
        eleve.pere = request.POST.get('pere')
        eleve.profession_pere = request.POST.get('profession_pere')
        eleve.contact_parent = request.POST.get('contact_parent')
        eleve.mere = request.POST.get('mere')
        eleve.profession_mere = request.POST.get('profession_mere')
        eleve.contact_mere = request.POST.get('contact_mere')
        # Si une nouvelle photo est téléchargée, l'associer à l'élève
        photo = request.FILES.get('photo')
        if photo:
            eleve.photo = photo
        # Sauvegarder les changements
        eleve.save()
        # Ajouter un message de succès
        messages.success(request, "Les informations de l'élève ont été mises à jour avec succès.")
        return redirect('eleve')  # Rediriger vers la liste des élèves
    else:
        # Si la méthode n'est pas POST, afficher le formulaire avec les données actuelles
        niveaux = Niveau.objects.all()
        groupes = GroupeClasse.objects.all()
        annees_scolaires = AnneeScolaire.objects.all()
        context = {
            'eleve': eleve,
            'niveaux': niveaux,
            'groupes': groupes,
            'annees_scolaires': annees_scolaires,
        }
        # Ajouter l'action dans l'historique
        Historique.objects.create(
            user=request.user,
            action=f"A modifié les informations de l'élève {eleve.prenom} {eleve.nom} "
                f"en {eleve.niveau.nom if eleve.niveau else 'N/A'} "
                f"pour l'année {eleve.annee_scolaire.nom if eleve.annee_scolaire else 'N/A'}"
        )
        return render(request, 'eleve/modifier_eleve.html', context)
        
#FONCTION DE SUPPRESSION DES INFORMATIONS
def supprimer(request, pk):
    eleve = get_object_or_404(Eleve, id=pk)

    # Enregistrer l'action dans l'historique avant suppression
    Historique.objects.create(
        user=request.user,
        action=f"A supprimé l'élève {eleve.prenom} {eleve.nom} "
               f"en {eleve.niveau.nom if eleve.niveau else 'N/A'} "
               f"pour l'année {eleve.annee_scolaire.nom if eleve.annee_scolaire else 'N/A'}"
    )

    eleve.delete()
    messages.success(request, f"L'élève {eleve.prenom} {eleve.nom} a été supprimé avec succès.")
    return redirect('eleve')


#FONCTION DE PAIEMENT ET RECU DE PAIEMENT DES FRAIS SCOLARITES

#SELECTIONNER L'ELEVE ANVANT D'EFFETUER SON PAIEMENT
def eleve_selection(request):
    # Récupérer les élèves en fonction de l'année scolaire et du niveau sélectionnés
    annees_scolaires = AnneeScolaire.objects.all()
    niveaux = Niveau.objects.all()
    groupeclasses = GroupeClasse.objects.all()

    eleves = Eleve.objects.all()
    # Filtrage des élèves par année scolaire, niveau et groupe classe, si ces paramètres sont envoyés via POST
    if request.method == "POST":
        annee_scolaire_nom = request.POST.get("annee_scolaire")
        niveau_nom = request.POST.get("niveau")
        groupeclasse_nom = request.POST.get("groupeclasse")

        if annee_scolaire_nom:
            eleves = eleves.filter(annee_scolaire__nom=annee_scolaire_nom)

        if niveau_nom:
            eleves = eleves.filter(niveau__nom=niveau_nom)

        if groupeclasse_nom:
            eleves = eleves.filter(groupe_classe__nom=groupeclasse_nom)

    # Pour chaque élève, récupérer les frais scolaires de l'année scolaire et du niveau
    eleves_frais = []
    for eleve in eleves:
        frais = FraisScolarite.objects.filter(eleve=eleve, annee_scolaire=eleve.annee_scolaire).first()  # On récupère le premier frais scolaire
        eleves_frais.append({
            'eleve': eleve,
            'frais': frais
        })

    return render(request, 'eleve/configuration_niveaux.html', {
        'eleves_frais': eleves_frais,
        'annees_scolaires': annees_scolaires,
        'niveaux': niveaux,
        'groupeclasses': groupeclasses
    })

from decimal import Decimal
from django.utils import timezone

def effectuer_paiement(request):
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve_id')
        montant = request.POST.get('montant')
        tranche = int(request.POST.get('tranche'))
        date_paiement = request.POST.get('date_paiement') or timezone.now().date()

        if not eleve_id or not montant or tranche is None:
            messages.error(request, "Les données du formulaire sont manquantes ou incorrectes.")
            return redirect('configuration')

        montant = Decimal(montant)

        if montant <= 0:
            messages.error(request, "Le montant du paiement doit être supérieur à 0.")
            return redirect('configuration')

        try:
            eleve = Eleve.objects.get(id=eleve_id)
            frais = FraisScolarite.objects.get(eleve=eleve)

            if frais.montant_total <= (frais.tranche1 + frais.tranche2 + frais.tranche3):
                messages.warning(request, f"L'élève {eleve.nom} a déjà payé la totalité des frais.")
                return redirect('configuration')

            recu = frais.enregistrer_paiement(montant, tranche)

            if recu:
                # Enregistrer l'action dans l'historique
                Historique.objects.create(
                    user=request.user,
                    action=f"A enregistré un paiement de {montant} GNF "
                           f"pour l'élève {eleve.prenom} {eleve.nom} "
                           f"(tranche {tranche}) le {date_paiement}"
                )

                messages.success(request, f"Paiement de {montant} GNF enregistré avec succès pour l'élève {eleve.nom}.")
                return redirect('afficher_recu', recu_id=recu.id)

        except Eleve.DoesNotExist:
            messages.error(request, "Élève introuvable.")
        except FraisScolarite.DoesNotExist:
            messages.error(request, "Frais scolaires non trouvés pour cet élève.")
        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {str(e)}")

        return redirect('configuration')

#RECU DE PAIEMENT DE LA DEUXIEME TRANCHE
def afficher_recu(request, recu_id):
        recu = get_object_or_404(Recu, id=recu_id)
        return render(request, 'eleve/recu_paiement.html', {'recu': recu})

# STATUT PAIEMENT

def statut_paiement_eleve(request):
    # Récupérer tous les niveaux, groupes et années scolaires pour les filtres
    niveaux = Niveau.objects.all()
    groupes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    # Récupérer les paramètres de filtrage depuis la requête GET
    niveau_id = request.GET.get('niveau')
    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')

    # Filtrer les élèves selon les paramètres de filtrage
    eleves = Eleve.objects.all()

    if niveau_id:
        eleves = eleves.filter(niveau__id=niveau_id)  # Utiliser l'ID du niveau
    if groupe_id:
        eleves = eleves.filter(groupe_classe__id=groupe_id)  # Utiliser l'ID du groupe
    if annee_id:
        eleves = eleves.filter(annee_scolaire__id=annee_id)  # Utiliser l'ID de l'année scolaire

    # Récupérer les informations des frais pour chaque élève
    eleves_info = []
    for eleve in eleves:
        frais_scolarite = FraisScolarite.objects.filter(eleve=eleve).first()

        if frais_scolarite:
            if frais_scolarite.solde == 0:
                statut_paiement = 'Paiement complet'
            elif frais_scolarite.total_paye > 0 and frais_scolarite.total_paye < frais_scolarite.montant_total:
                statut_paiement = 'Paiement partiel'
            else:
                statut_paiement = 'En attente de paiement'
        else:
            statut_paiement = 'Aucune donnée de paiement'

        eleves_info.append({
            'eleve': eleve,
            'statut_paiement': statut_paiement,
        })

    # Rendre le résultat dans un template
    return render(request, 'eleve/statut_paiement_eleve.html', {
        'eleves_info': eleves_info,
        'niveaux': niveaux,
        'groupes': groupes,
        'annees_scolaires': annees_scolaires,
    })


def get_groupe(request):
    niveau_id = request.GET.get('niveau')
    groupes = list(GroupeClasse.objects.filter(niveau_id=niveau_id).values('id', 'nom'))
    return JsonResponse({'groupes': groupes})


#DETAILS DES INFORMATIONS D'ELEVES
def detail_eleve(request, pk):
    # Récupérer l'élève avec l'ID passé en paramètre
    eleve = get_object_or_404(Eleve, id=pk)
    return render(request, 'eleve/detail_eleve.html', {'eleve': eleve})

#afficher les eleves par niveau et annee scolaire

def liste_eleves_par_niveau_annee(request):
    niveau_id = request.GET.get('niveau')
    annee_id = request.GET.get('annee_scolaire')

    eleves = Eleve.objects.filter(actif=True)
    niveaux = Niveau.objects.all()
    annees = AnneeScolaire.objects.all()

    if niveau_id:
        eleves = eleves.filter(niveau_id=niveau_id)
    
    if annee_id:
        eleves = eleves.filter(annee_scolaire_id=annee_id)

    return render(request, 'eleve/liste_eleves_par_niveau_annee.html', {
        'eleves': eleves,
        'niveaux': niveaux,
        'annees': annees,
    })


#AFFICHER LES LES ELEVES PAR GROUPE DE CLASSE OU OPTION ET ANNEE SCOlAIRE

def liste_eleves_par_groupe(request):
    groupes = GroupeClasse.objects.all()
    annees = AnneeScolaire.objects.all()

    groupe_id = request.GET.get('groupe')
    annee_id = request.GET.get('annee_scolaire')

    # Filtrer les élèves en fonction des valeurs sélectionnées
    eleves = Eleve.objects.all()

    if groupe_id:
        eleves = eleves.filter(groupe_classe__id=groupe_id)  # Correction ici

    if annee_id:
        eleves = eleves.filter(annee_scolaire__id=annee_id)

    context = {
        'eleves': eleves,
        'groupes': groupes,
        'annees': annees
    }
    return render(request, 'eleve/liste_eleves_par_groupe.html', context)



def historique(request):
    
    if request.user.is_superuser:
        # Super utilisateur : voir tous les historiques
        historiques = Historique.objects.all().order_by('-created_time')
    else:
        # Utilisateur normal : voir uniquement ses propres actions
        historiques = Historique.objects.filter(user=request.user).order_by('-created_time')

    return render(request, 'eleve/historique.html', {'historiques': historiques})


def profiles(request):

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

        return redirect("profiles")
    
    context = {
        "user": user,
    }
    return render(request,'eleve/profil.html',context)

###################################################################
#LES DROIT DU FONDATEUR
# #################################################################


# STATUT PAIEMENT

def statut_paiement_eleve_fondateur(request):
    # Récupérer tous les niveaux, groupes et années scolaires pour les filtres
    niveaux = Niveau.objects.all()
    groupes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    # Récupérer les paramètres de filtrage depuis la requête GET
    niveau_id = request.GET.get('niveau')
    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')

    # Filtrer les élèves selon les paramètres de filtrage
    eleves = Eleve.objects.all()

    if niveau_id:
        eleves = eleves.filter(niveau__id=niveau_id)  # Utiliser l'ID du niveau
    if groupe_id:
        eleves = eleves.filter(groupe_classe__id=groupe_id)  # Utiliser l'ID du groupe
    if annee_id:
        eleves = eleves.filter(annee_scolaire__id=annee_id)  # Utiliser l'ID de l'année scolaire

    # Récupérer les informations des frais pour chaque élève
    eleves_info = []
    for eleve in eleves:
        frais_scolarite = FraisScolarite.objects.filter(eleve=eleve).first()

        if frais_scolarite:
            if frais_scolarite.solde == 0:
                statut_paiement = 'Paiement complet'
            elif frais_scolarite.total_paye > 0 and frais_scolarite.total_paye < frais_scolarite.montant_total:
                statut_paiement = 'Paiement partiel'
            else:
                statut_paiement = 'En attente de paiement'
        else:
            statut_paiement = 'Aucune donnée de paiement'

        eleves_info.append({
            'eleve': eleve,
            'statut_paiement': statut_paiement,
        })

    # Rendre le résultat dans un template
    return render(request, 'admin/statut_paiement_eleve.html', {
        'eleves_info': eleves_info,
        'niveaux': niveaux,
        'groupes': groupes,
        'annees_scolaires': annees_scolaires,
    })

#DETAILS DES INFORMATIONS D'ELEVES
def detail_eleves(request, pk):
    # Récupérer l'élève avec l'ID passé en paramètre
    eleve = get_object_or_404(Eleve, id=pk)
    return render(request, 'admin/detail_eleve.html', {'eleve': eleve})

#afficher les eleves par niveau et annee scolaire

def liste_eleves_par_niveau(request):
    niveau_id = request.GET.get('niveau')
    annee_id = request.GET.get('annee_scolaire')

    eleves = Eleve.objects.filter(actif=True)
    niveaux = Niveau.objects.all()
    annees = AnneeScolaire.objects.all()

    if niveau_id:
        eleves = eleves.filter(niveau_id=niveau_id)
    
    if annee_id:
        eleves = eleves.filter(annee_scolaire_id=annee_id)

    return render(request, 'admin/liste_eleves_par_niveau_annee.html', {
        'eleves': eleves,
        'niveaux': niveaux,
        'annees': annees,
    })


#AFFICHER LES LES ELEVES PAR GROUPE DE CLASSE OU OPTION ET ANNEE SCOlAIRE

def liste_eleves_par_classe(request):
    groupes = GroupeClasse.objects.all()
    annees = AnneeScolaire.objects.all()

    groupe_id = request.GET.get('groupe')
    annee_id = request.GET.get('annee_scolaire')

    # Filtrer les élèves en fonction des valeurs sélectionnées
    eleves = Eleve.objects.all()

    if groupe_id:
        eleves = eleves.filter(groupe_classe__id=groupe_id)  # Correction ici

    if annee_id:
        eleves = eleves.filter(annee_scolaire__id=annee_id)

    context = {
        'eleves': eleves,
        'groupes': groupes,
        'annees': annees
    }
    return render(request, 'admin/liste_eleves_par_groupe.html', context)

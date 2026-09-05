
# ============================================================
# IMPORTS
# ============================================================

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from annee_scolaire.models import AnneeScolaire
from cycle.models import Etablissement
from groupe_classe.models import GroupeClasse
from niveau.models import Niveau

from eleve.models import (
    Eleve,
    EleveInscrit,
    Recu,
    FraisScolarite,
)

from personnel.models import Administrateur, Historique


# ============================================================
# LISTE TOTALE DES ÉLÈVES
# ============================================================

@login_required
def liste_totale_eleve(request):

    niveaux = Niveau.objects.all().order_by('nom')
    groupes = GroupeClasse.objects.all().order_by('nom')
    annees = AnneeScolaire.objects.all().order_by('-id')

    eleves = (
        Eleve.objects
        .select_related(
            'niveau',
            'groupe_classe',
            'annee_scolaire'
        )
        .all()
        .order_by('nom', 'prenom')
    )

    context = {
        'eleves': eleves,
        'niveaus': niveaux,
        'groupes': groupes,
        'annes': annees,
    }

    return render(
        request,
        'eleve/liste_totale_eleve.html',
        context
    )


# ============================================================
# FORMULAIRE AJOUT ÉLÈVE
# ============================================================

@login_required
def formeleve(request):

    niveaux = Niveau.objects.all().order_by('nom')
    groupes = GroupeClasse.objects.all().order_by('nom')
    annees = AnneeScolaire.objects.all().order_by('-id')
    eleves = Eleve.objects.all().order_by('nom', 'prenom')

    context = {
        'eleves': eleves,
        'niveaus': niveaux,
        'groupes': groupes,
        'annes': annees,
    }

    return render(
        request,
        'eleve/ajout_eleve.html',
        context
    )


# ============================================================
# FORMULAIRE MODIFICATION
# ============================================================

@login_required
def forme_modifie(request):

    niveaux = Niveau.objects.all().order_by('nom')
    groupes = GroupeClasse.objects.all().order_by('nom')
    annees = AnneeScolaire.objects.all().order_by('-id')
    eleves = Eleve.objects.all().order_by('nom', 'prenom')

    context = {
        'eleves': eleves,
        'niveaus': niveaux,
        'groupes': groupes,
        'annes': annees,
    }

    return render(
        request,
        'eleve/ajout_modifier.html',
        context
    )


# ============================================================
# VALIDATION DATE DE NAISSANCE
# ============================================================

def validate_birthdate(value):

    if not value:
        raise ValidationError(
            "La date de naissance est obligatoire."
        )

    aujourd_hui = date.today()

    age = (
        aujourd_hui.year
        - value.year
        - (
            (aujourd_hui.month, aujourd_hui.day)
            < (value.month, value.day)
        )
    )

    if age < 8:

        raise ValidationError(
            "L'élève doit avoir au moins 8 ans."
        )

    if value > aujourd_hui:

        raise ValidationError(
            "La date de naissance ne peut pas être dans le futur."
        )


# ============================================================
# AJOUT D'UN ÉLÈVE
# ============================================================

@login_required
def ajout(request):

    if request.method != 'POST':

        return render(
            request,
            'eleve/ajout_eleve.html',
            {
                'niveaus': Niveau.objects.all().order_by('nom'),
                'groupes': GroupeClasse.objects.all().order_by('nom'),
                'annes': AnneeScolaire.objects.all().order_by('-id'),
            }
        )

    # ========================================================
    # RÉCUPÉRATION DES DONNÉES
    # ========================================================

    niveau_id = request.POST.get('nive')
    groupe_id = request.POST.get('group')
    annee_id = request.POST.get('anne')

    nom = request.POST.get('nom', '').strip()
    prenom = request.POST.get('prenom', '').strip()
    genre = request.POST.get('sexe', '').strip()
    contact = request.POST.get('contact', '').strip()

    photo = request.FILES.get('photo')

    naissance = request.POST.get('date')
    lieu = request.POST.get('lieu', '').strip()

    pere = request.POST.get('pere', '').strip()
    fonction_pere = request.POST.get('fp', '').strip()
    contact_pere = request.POST.get('cp', '').strip()

    mere = request.POST.get('mere', '').strip()
    fonction_mere = request.POST.get('fm', '').strip()
    contact_mere = request.POST.get('cm', '').strip()

    # ========================================================
    # VÉRIFICATION DES CHAMPS OBLIGATOIRES
    # ========================================================

    if not nom or not prenom:

        messages.error(
            request,
            "Le nom et le prénom sont obligatoires."
        )

        return redirect('forme')

    if not niveau_id or not groupe_id or not annee_id:

        messages.error(
            request,
            "Le niveau, la classe et l'année scolaire sont obligatoires."
        )

        return redirect('forme')

    if not naissance:

        messages.error(
            request,
            "La date de naissance est obligatoire."
        )

        return redirect('forme')

    # ========================================================
    # DATE DE NAISSANCE
    # ========================================================

    try:

        naissance_date = date.fromisoformat(
            naissance
        )

        validate_birthdate(
            naissance_date
        )

    except ValueError:

        messages.error(
            request,
            "La date de naissance est invalide."
        )

        return redirect('forme')

    except ValidationError as e:

        messages.error(
            request,
            e.message
        )

        return redirect('forme')

    # ========================================================
    # RÉCUPÉRATION DES OBJETS
    # ========================================================

    niveau_obj = get_object_or_404(
        Niveau,
        id=niveau_id
    )

    groupe_obj = get_object_or_404(
        GroupeClasse,
        id=groupe_id
    )

    annee_obj = get_object_or_404(
        AnneeScolaire,
        id=annee_id
    )

    # ========================================================
    # VÉRIFIER QUE LA CLASSE APPARTIENT AU NIVEAU
    # ========================================================

    if groupe_obj.niveau_id != niveau_obj.id:

        messages.error(
            request,
            "La classe sélectionnée ne correspond pas au niveau choisi."
        )

        return redirect('forme')

    # ========================================================
    # RECHERCHE D'UN ÉLÈVE EXISTANT
    # ========================================================

    eleve_existant = Eleve.objects.filter(
        nom__iexact=nom,
        prenom__iexact=prenom,
        date_naissance=naissance_date
    ).first()

    if eleve_existant:

        inscription_existante = EleveInscrit.objects.filter(
            eleve=eleve_existant,
            annee_scolaire=annee_obj
        ).exists()

        if inscription_existante:

            messages.error(
                request,
                "Cet élève est déjà inscrit pour cette année scolaire."
            )

            return redirect('forme')

    # ========================================================
    # CRÉATION DE L'ÉLÈVE
    # ========================================================

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

        contact_mere=contact_mere,
        mere=mere,
        profession_mere=fonction_mere,

        profession_pere=fonction_pere,
        pere=pere,
        contact_parent=contact_pere,

        actif=True
    )

    # ========================================================
    # CRÉATION DE L'INSCRIPTION
    # ========================================================

    inscription, created = EleveInscrit.objects.get_or_create(
        eleve=eleve,
        annee_scolaire=annee_obj,
        defaults={
            'niveau': niveau_obj,
            'groupe_classe': groupe_obj,
            'actif': True,
        }
    )

    if not created:

        inscription.niveau = niveau_obj
        inscription.groupe_classe = groupe_obj
        inscription.actif = True
        inscription.save()

    # ========================================================
    # FRAIS DE SCOLARITÉ
    # ========================================================

    montant_total = (
        niveau_obj.montant_frais
        or Decimal('0')
    )

    frais, frais_created = FraisScolarite.objects.get_or_create(
        eleve=eleve,
        annee_scolaire=annee_obj,
        defaults={
            'montant_total': montant_total,
            'tranche1': Decimal('0'),
            'tranche2': Decimal('0'),
            'tranche3': Decimal('0'),
            'total_paye': Decimal('0'),
            'solde': montant_total,
            'est_paye': False,
        }
    )

    # ========================================================
    # HISTORIQUE
    # ========================================================

    Historique.objects.create(
        user=request.user,
        action=(
            f"A ajouté l'élève {prenom} {nom} "
            f"en {niveau_obj.nom} "
            f"pour l'année {annee_obj.nom}"
        )
    )

    # ========================================================
    # MESSAGE
    # ========================================================

    messages.success(
        request,
        (
            f"L'élève {prenom} {nom} a été ajouté avec succès. "
            f"Matricule : {eleve.matricule}"
        )
    )

    return redirect('forme')


# ============================================================
# AJAX : GROUPES D'UN NIVEAU
# ============================================================

@login_required
def get_groupes(request):

    niveau_id = request.GET.get('niveau')

    if not niveau_id:

        return JsonResponse({
            'groupes': []
        })

    groupes = (
        GroupeClasse.objects
        .filter(niveau_id=niveau_id)
        .order_by('nom')
        .values(
            'id',
            'nom'
        )
    )

    return JsonResponse({
        'groupes': list(groupes)
    })


# ============================================================
# MODIFICATION D'UN ÉLÈVE
# ============================================================

@login_required
def modifier(request, pk):

    # ========================================================
    # IMPORTANT
    # ========================================================
    # Le pk correspond à EleveInscrit.id
    # et non à Eleve.id.
    # ========================================================

    eleve_inscrit = get_object_or_404(
        EleveInscrit.objects.select_related(
            'eleve',
            'niveau',
            'groupe_classe',
            'annee_scolaire'
        ),
        pk=pk
    )

    # Élève réel
    eleve = eleve_inscrit.eleve

    # ========================================================
    # POST
    # ========================================================

    if request.method == 'POST':

        # ====================================================
        # DONNÉES SCOLAIRES
        # ====================================================

        niveau_id = request.POST.get('niveau')
        groupe_classe_id = request.POST.get('groupe_classe')
        annee_scolaire_id = request.POST.get('annee_scolaire')

        if not niveau_id or not groupe_classe_id or not annee_scolaire_id:

            messages.error(
                request,
                "Le niveau, la classe et l'année scolaire sont obligatoires."
            )

            return redirect(
                'modifier_eleve',
                pk=pk
            )

        # ====================================================
        # RÉCUPÉRATION DES OBJETS
        # ====================================================

        try:

            niveau = Niveau.objects.get(
                pk=int(niveau_id)
            )

            groupe_classe = GroupeClasse.objects.get(
                pk=int(groupe_classe_id)
            )

            annee_scolaire = AnneeScolaire.objects.get(
                pk=int(annee_scolaire_id)
            )

        except ValueError:

            messages.error(
                request,
                "Les informations scolaires sélectionnées sont invalides."
            )

            return redirect(
                'modifier_eleve',
                pk=pk
            )

        except Niveau.DoesNotExist:

            messages.error(
                request,
                "Le niveau sélectionné n'existe pas."
            )

            return redirect(
                'modifier_eleve',
                pk=pk
            )

        except GroupeClasse.DoesNotExist:

            messages.error(
                request,
                "La classe sélectionnée n'existe pas."
            )

            return redirect(
                'modifier_eleve',
                pk=pk
            )

        except AnneeScolaire.DoesNotExist:

            messages.error(
                request,
                "L'année scolaire sélectionnée n'existe pas."
            )

            return redirect(
                'modifier_eleve',
                pk=pk
            )

        # ====================================================
        # VÉRIFICATION NIVEAU / CLASSE
        # ====================================================

        if groupe_classe.niveau_id != niveau.id:

            messages.error(
                request,
                "La classe sélectionnée ne correspond pas au niveau choisi."
            )

            return redirect(
                'modifier_eleve',
                pk=pk
            )

        # ====================================================
        # VÉRIFICATION ANNÉE SCOLAIRE
        # ====================================================
        # Un élève ne peut avoir qu'une seule inscription
        # pour une même année scolaire.
        # ====================================================

        inscription_existante = (
            EleveInscrit.objects
            .filter(
                eleve=eleve,
                annee_scolaire=annee_scolaire
            )
            .exclude(
                pk=eleve_inscrit.pk
            )
            .first()
        )

        if inscription_existante:

            messages.error(
                request,
                (
                    f"Cet élève possède déjà une inscription "
                    f"pour l'année scolaire "
                    f"{annee_scolaire.nom}."
                )
            )

            return redirect(
                'modifier_eleve',
                pk=pk
            )

        # ====================================================
        # INFORMATIONS PERSONNELLES
        # ====================================================

        nom = request.POST.get(
            'nom',
            ''
        ).strip()

        prenom = request.POST.get(
            'prenom',
            ''
        ).strip()

        lieu_naissance = request.POST.get(
            'lieu_naissance',
            ''
        ).strip()

        genre = request.POST.get(
            'genre',
            ''
        ).strip()

        telephone = request.POST.get(
            'telephone',
            ''
        ).strip()

        # ====================================================
        # VALIDATION NOM / PRÉNOM
        # ====================================================

        if not nom or not prenom:

            messages.error(
                request,
                "Le nom et le prénom sont obligatoires."
            )

            return redirect(
                'modifier_eleve',
                pk=pk
            )

        # ====================================================
        # DATE DE NAISSANCE
        # ====================================================

        date_naissance_value = request.POST.get(
            'date_naissance',
            ''
        ).strip()

        date_naissance_obj = eleve.date_naissance

        if date_naissance_value:

            try:

                date_naissance_obj = date.fromisoformat(
                    date_naissance_value
                )

                validate_birthdate(
                    date_naissance_obj
                )

            except ValueError:

                messages.error(
                    request,
                    "La date de naissance est invalide."
                )

                return redirect(
                    'modifier_eleve',
                    pk=pk
                )

            except ValidationError as e:

                messages.error(
                    request,
                    e.message
                )

                return redirect(
                    'modifier_eleve',
                    pk=pk
                )

        # ====================================================
        # INFORMATIONS DU PÈRE
        # ====================================================

        pere = request.POST.get(
            'pere',
            ''
        ).strip()

        profession_pere = request.POST.get(
            'profession_pere',
            ''
        ).strip()

        contact_parent = request.POST.get(
            'contact_parent',
            ''
        ).strip()

        # ====================================================
        # INFORMATIONS DE LA MÈRE
        # ====================================================

        mere = request.POST.get(
            'mere',
            ''
        ).strip()

        profession_mere = request.POST.get(
            'profession_mere',
            ''
        ).strip()

        contact_mere = request.POST.get(
            'contact_mere',
            ''
        ).strip()

        # ====================================================
        # PHOTO
        # ====================================================

        nouvelle_photo = request.FILES.get(
            'photo'
        )

        # ====================================================
        # SAUVEGARDE DE L'INSCRIPTION
        # ====================================================
        # IMPORTANT :
        # On modifie UNIQUEMENT cette inscription.
        #
        # Les autres inscriptions de l'élève ne sont pas
        # touchées.
        # ====================================================

        ancien_niveau = eleve_inscrit.niveau
        ancienne_classe = eleve_inscrit.groupe_classe
        ancienne_annee = eleve_inscrit.annee_scolaire

        eleve_inscrit.niveau = niveau
        eleve_inscrit.groupe_classe = groupe_classe
        eleve_inscrit.annee_scolaire = annee_scolaire
        eleve_inscrit.actif = True

        eleve_inscrit.save()

        # ====================================================
        # MISE À JOUR DES INFORMATIONS PERSONNELLES
        # ====================================================
        # Ces informations appartiennent à l'élève lui-même.
        # ====================================================

        eleve.nom = nom
        eleve.prenom = prenom
        eleve.date_naissance = date_naissance_obj
        eleve.lieu_naissance = lieu_naissance
        eleve.genre = genre
        eleve.telephone = telephone

        # ====================================================
        # PÈRE
        # ====================================================

        eleve.pere = pere
        eleve.profession_pere = profession_pere
        eleve.contact_parent = contact_parent

        # ====================================================
        # MÈRE
        # ====================================================

        eleve.mere = mere
        eleve.profession_mere = profession_mere
        eleve.contact_mere = contact_mere

        # ====================================================
        # PHOTO
        # ====================================================

        if nouvelle_photo:
            eleve.photo = nouvelle_photo

        # ====================================================
        # IMPORTANT
        # ====================================================
        # NE PAS FAIRE :
        #
        # eleve.niveau = niveau
        # eleve.groupe_classe = groupe_classe
        # eleve.annee_scolaire = annee_scolaire
        #
        # Ces informations appartiennent à EleveInscrit.
        # ====================================================

        eleve.save()

        # ====================================================
        # FRAIS DE SCOLARITÉ
        # ====================================================
        # Les frais sont liés à l'élève + à l'année scolaire.
        # ====================================================

        montant_total = (
            niveau.montant_frais
            if niveau.montant_frais is not None
            else Decimal('0')
        )

        frais, created = FraisScolarite.objects.get_or_create(
            eleve=eleve,
            annee_scolaire=annee_scolaire,
            defaults={
                'montant_total': montant_total,
                'tranche1': Decimal('0'),
                'tranche2': Decimal('0'),
                'tranche3': Decimal('0'),
                'total_paye': Decimal('0'),
                'solde': montant_total,
                'est_paye': False,
            }
        )

        # ====================================================
        # SI LES FRAIS EXISTENT DÉJÀ
        # ====================================================
        # On conserve les paiements déjà effectués.
        # ====================================================

        if not created:

            frais.montant_total = montant_total

            frais.solde = (
                montant_total - frais.total_paye
            )

            frais.est_paye = (
                frais.total_paye >= montant_total
            )

            frais.save()

        # ====================================================
        # HISTORIQUE
        # ====================================================

        ancien_niveau_nom = (
            ancien_niveau.nom
            if ancien_niveau
            else 'N/A'
        )

        ancien_classe_nom = (
            ancienne_classe.nom
            if ancienne_classe
            else 'N/A'
        )

        ancienne_annee_nom = (
            ancienne_annee.nom
            if ancienne_annee
            else 'N/A'
        )

        nouveau_niveau_nom = (
            niveau.nom
            if niveau
            else 'N/A'
        )

        nouvelle_classe_nom = (
            groupe_classe.nom
            if groupe_classe
            else 'N/A'
        )

        nouvelle_annee_nom = (
            annee_scolaire.nom
            if annee_scolaire
            else 'N/A'
        )

        Historique.objects.create(
            user=request.user,
            action=(
                f"A modifié l'inscription de l'élève "
                f"{eleve.prenom} {eleve.nom}. "
                f"Ancienne inscription : "
                f"{ancien_niveau_nom} / "
                f"{ancien_classe_nom} / "
                f"{ancienne_annee_nom}. "
                f"Nouvelle inscription : "
                f"{nouveau_niveau_nom} / "
                f"{nouvelle_classe_nom} / "
                f"{nouvelle_annee_nom}."
            )
        )

        # ====================================================
        # MESSAGE DE SUCCÈS
        # ====================================================

        if nouvelle_photo:

            messages.success(
                request,
                (
                    "Les informations de l'élève, son inscription "
                    "et sa photo ont été mises à jour avec succès."
                )
            )

        else:

            messages.success(
                request,
                (
                    "Les informations de l'élève et son inscription "
                    "ont été mises à jour avec succès."
                )
            )

        # ====================================================
        # REDIRECTION
        # ====================================================

        return redirect(
            'eleve'
        )

    # ========================================================
    # DONNÉES DU FORMULAIRE
    # ========================================================

    niveaux = (
        Niveau.objects
        .all()
        .order_by('nom')
    )

    groupes = (
        GroupeClasse.objects
        .select_related('niveau')
        .all()
        .order_by('nom')
    )

    annees_scolaires = (
        AnneeScolaire.objects
        .all()
        .order_by('-id')
    )

    # ========================================================
    # CONTEXTE
    # ========================================================

    context = {
        # Le template utilise :
        # eleve.eleve.nom
        # eleve.eleve.prenom
        #
        # Donc on transmet EleveInscrit.

        'eleve': eleve_inscrit,

        'niveaux': niveaux,

        'groupes': groupes,

        'annees_scolaires': annees_scolaires,
    }

    # ========================================================
    # AFFICHAGE
    # ========================================================

    return render(
        request,
        'eleve/modifier_eleve.html',
        context
    )




# ============================================================
# SUPPRESSION D'UN ÉLÈVE
# ============================================================

@login_required
def supprimer(request, pk):

    eleve = get_object_or_404(
        Eleve,
        id=pk
    )

    nom_complet = f"{eleve.prenom} {eleve.nom}"

    niveau_nom = (
        eleve.niveau.nom
        if eleve.niveau
        else 'N/A'
    )

    annee_nom = (
        eleve.annee_scolaire.nom
        if eleve.annee_scolaire
        else 'N/A'
    )

    # ========================================================
    # HISTORIQUE AVANT SUPPRESSION
    # ========================================================

    Historique.objects.create(
        user=request.user,
        action=(
            f"A supprimé l'élève {nom_complet} "
            f"en {niveau_nom} "
            f"pour l'année {annee_nom}"
        )
    )

    # ========================================================
    # SUPPRESSION
    # ========================================================

    eleve.delete()

    messages.success(
        request,
        f"L'élève {nom_complet} a été supprimé avec succès."
    )

    return redirect(
        'eleve'
    )


# ============================================================

# SÉLECTION DES ÉLÈVES POUR PAIEMENT

# ============================================================

@login_required
def eleve_selection(request):


    # ========================================================
    # ANNÉES SCOLAIRES
    # ========================================================

    annees_scolaires = (
        AnneeScolaire.objects
        .all()
        .order_by('-id')
    )


    # ========================================================
    # NIVEAUX
    # ========================================================

    niveaux = (
        Niveau.objects
        .all()
        .order_by('nom')
    )


    # ========================================================
    # GROUPES CLASSES
    # ========================================================

    groupeclasses = (
        GroupeClasse.objects
        .all()
        .order_by('nom')
    )


    # ========================================================
    # INSCRIPTIONS
    # ========================================================
    # On travaille directement avec EleveInscrit.
    #
    # Chaque inscription correspond à un élève pour une
    # année scolaire donnée, avec son niveau et sa classe.
    # ========================================================

    inscriptions = (
        EleveInscrit.objects
        .select_related(
            'eleve',
            'annee_scolaire',
            'niveau',
            'groupe_classe'
        )
        .filter(
            actif=True
        )
        .order_by(
            'eleve__nom',
            'eleve__prenom'
        )
    )


    # ========================================================
    # RÉCUPÉRATION DES FILTRES
    # ========================================================

    annee_scolaire_id = request.GET.get(
        'annee_scolaire'
    )

    niveau_id = request.GET.get(
        'niveau'
    )

    groupeclasse_id = request.GET.get(
        'groupeclasse'
    )


    # ========================================================
    # FILTRE ANNÉE SCOLAIRE
    # ========================================================

    if annee_scolaire_id:

        inscriptions = inscriptions.filter(
            annee_scolaire_id=annee_scolaire_id
        )


    # ========================================================
    # FILTRE NIVEAU
    # ========================================================

    if niveau_id:

        inscriptions = inscriptions.filter(
            niveau_id=niveau_id
        )


    # ========================================================
    # FILTRE GROUPE CLASSE
    # ========================================================

    if groupeclasse_id:

        inscriptions = inscriptions.filter(
            groupe_classe_id=groupeclasse_id
        )


    # ========================================================
    # FRAIS DE SCOLARITÉ
    # ========================================================

    eleves_frais = []


    for inscription in inscriptions:

        # ----------------------------------------------------
        # Recherche des frais correspondant exactement à
        # l'élève ET à l'année scolaire de son inscription.
        # ----------------------------------------------------

        frais = (
            FraisScolarite.objects
            .filter(
                eleve=inscription.eleve,
                annee_scolaire=inscription.annee_scolaire
            )
            .first()
        )


        # ----------------------------------------------------
        # On conserve l'inscription comme objet principal.
        # Le template peut ensuite accéder à :
        #
        # item.inscription.eleve
        # item.inscription.annee_scolaire
        # item.inscription.niveau
        # item.inscription.groupe_classe
        # ----------------------------------------------------

        eleves_frais.append({

            'inscription': inscription,

            'frais': frais,

        })


    # ========================================================
    # CONTEXTE
    # ========================================================

    context = {

        'eleves_frais': eleves_frais,

        'annees_scolaires': annees_scolaires,

        'niveaux': niveaux,

        'groupeclasses': groupeclasses,

        'selected_annee_id': annee_scolaire_id,

        'selected_niveau_id': niveau_id,

        'selected_groupe_id': groupeclasse_id,

        'today': timezone.now().date(),

    }


    # ========================================================
    # AFFICHAGE
    # ========================================================

    return render(

        request,

        'eleve/configuration_niveaux.html',

        context

)



# ============================================================
# EFFECTUER UN PAIEMENT
# ============================================================

@login_required
def effectuer_paiement(request):

    if request.method != 'POST':

        return redirect(
            'configuration'
        )

    # ========================================================
    # DONNÉES
    # ========================================================

    inscription_id = request.POST.get(
        'inscription_id'
    )

    montant_str = request.POST.get(
        'montant'
    )

    tranche_str = request.POST.get(
        'tranche'
    )

    date_paiement = request.POST.get(
        'date_paiement'
    )

    # ========================================================
    # INSCRIPTION
    # ========================================================

    if not inscription_id:

        messages.error(
            request,
            "L'inscription de l'élève est manquante."
        )

        return redirect(
            'configuration'
        )

    # ========================================================
    # MONTANT
    # ========================================================

    if not montant_str:

        messages.error(
            request,
            "Le montant du paiement est obligatoire."
        )

        return redirect(
            'configuration'
        )

    try:

        montant = Decimal(
            str(montant_str).replace(',', '.')
        )

    except (InvalidOperation, ValueError, TypeError):

        messages.error(
            request,
            "Le montant du paiement est invalide."
        )

        return redirect(
            'configuration'
        )

    if montant <= 0:

        messages.error(
            request,
            "Le montant doit être supérieur à 0."
        )

        return redirect(
            'configuration'
        )

    # ========================================================
    # TRANCHE
    # ========================================================

    if not tranche_str:

        messages.error(
            request,
            "Veuillez sélectionner une tranche."
        )

        return redirect(
            'configuration'
        )

    try:

        tranche = int(
            tranche_str
        )

    except (ValueError, TypeError):

        messages.error(
            request,
            "La tranche sélectionnée est invalide."
        )

        return redirect(
            'configuration'
        )

    if tranche not in [1, 2, 3]:

        messages.error(
            request,
            "La tranche doit être 1, 2 ou 3."
        )

        return redirect(
            'configuration'
        )

    # ========================================================
    # DATE
    # ========================================================

    if not date_paiement:

        date_paiement = timezone.now().date()

    # ========================================================
    # INSCRIPTION
    # ========================================================

    inscription = get_object_or_404(
        EleveInscrit.objects.select_related(
            'eleve',
            'annee_scolaire',
            'niveau',
            'groupe_classe'
        ),
        id=inscription_id
    )

    eleve = inscription.eleve
    annee_scolaire = inscription.annee_scolaire

    # ========================================================
    # FRAIS
    # ========================================================

    frais = (
        FraisScolarite.objects
        .filter(
            eleve=eleve,
            annee_scolaire=annee_scolaire
        )
        .first()
    )

    # ========================================================
    # CRÉER LES FRAIS SI NÉCESSAIRE
    # ========================================================

    if not frais:

        montant_total = Decimal('0')

        if inscription.niveau:

            montant_total = (
                inscription.niveau.montant_frais
                or Decimal('0')
            )

        if montant_total <= 0:

            messages.error(
                request,
                (
                    f"Aucun montant de frais n'est défini "
                    f"pour le niveau de {eleve.prenom} {eleve.nom}."
                )
            )

            return redirect(
                'configuration'
            )

        frais = FraisScolarite.objects.create(
            eleve=eleve,
            annee_scolaire=annee_scolaire,

            montant_total=montant_total,

            tranche1=Decimal('0'),
            tranche2=Decimal('0'),
            tranche3=Decimal('0'),

            total_paye=Decimal('0'),
            solde=montant_total,

            est_paye=False,
        )

    # ========================================================
    # CALCUL DU SOLDE
    # ========================================================

    montant_total = (
        frais.montant_total
        or Decimal('0')
    )

    total_paye = (
        frais.total_paye
        or Decimal('0')
    )

    montant_restant = (
        montant_total
        - total_paye
    )

    if montant_restant < 0:

        montant_restant = Decimal('0')

    # ========================================================
    # DÉJÀ PAYÉ
    # ========================================================

    if montant_restant <= 0:

        messages.warning(
            request,
            (
                f"{eleve.prenom} {eleve.nom} "
                f"a déjà payé la totalité des frais "
                f"pour {annee_scolaire.nom}."
            )
        )

        return redirect(
            'configuration'
        )

    # ========================================================
    # PAIEMENT SUPÉRIEUR AU SOLDE
    # ========================================================

    if montant > montant_restant:

        messages.error(
            request,
            (
                f"Le montant saisi est de {montant} GNF, "
                f"mais le montant restant est de "
                f"{montant_restant} GNF."
            )
        )

        return redirect(
            'configuration'
        )

    # ========================================================
    # ENREGISTREMENT
    # ========================================================

    try:

        recu = frais.enregistrer_paiement(
            montant,
            tranche
        )

    except ValueError as e:

        messages.error(
            request,
            str(e)
        )

        return redirect(
            'configuration'
        )

    except Exception as e:

        messages.error(
            request,
            (
                "Une erreur est survenue lors de "
                f"l'enregistrement du paiement : {e}"
            )
        )

        return redirect(
            'configuration'
        )

    # ========================================================
    # VÉRIFIER LE REÇU
    # ========================================================

    if not recu:

        messages.error(
            request,
            "Le paiement n'a pas pu être enregistré."
        )

        return redirect(
            'configuration'
        )

    # ========================================================
    # HISTORIQUE
    # ========================================================

    Historique.objects.create(
        user=request.user,
        action=(
            f"A enregistré un paiement de {montant} GNF "
            f"pour l'élève "
            f"{eleve.prenom} {eleve.nom} "
            f"(matricule : {eleve.matricule}) "
            f"(tranche {tranche}) "
            f"pour l'année scolaire "
            f"{annee_scolaire.nom} "
            f"le {date_paiement}"
        )
    )

    # ========================================================
    # MESSAGE
    # ========================================================

    messages.success(
        request,
        (
            f"Paiement de {montant} GNF enregistré avec succès "
            f"pour {eleve.prenom} {eleve.nom}."
        )
    )

    # ========================================================
    # REÇU
    # ========================================================

    return redirect(
        'afficher_recu',
        recu_id=recu.id
    )


# ============================================================
# AFFICHER UN REÇU
# ============================================================

@login_required
def afficher_recu(request, recu_id):

    ecoles = Etablissement.objects.all()

    recu = get_object_or_404(
        Recu.objects.select_related(
            'frais_scolarite',
            'frais_scolarite__eleve',
            'frais_scolarite__annee_scolaire'
        ),
        id=recu_id
    )

    return render(
        request,
        'eleve/recu_paiement.html',
        {
            'recu': recu,
            'ecoles': ecoles,
        }
    )


# ============================================================
# STATUT DES PAIEMENTS
# ============================================================

@login_required
def statut_paiement_eleve(request):

    niveaux = (
        Niveau.objects
        .all()
        .order_by('nom')
    )

    groupes = (
        GroupeClasse.objects
        .all()
        .order_by('nom')
    )

    annees_scolaires = (
        AnneeScolaire.objects
        .all()
        .order_by('-id')
    )

    ecoles = Etablissement.objects.all()

    # ========================================================
    # FILTRES
    # ========================================================

    niveau_id = request.GET.get(
        'niveau'
    )

    groupe_id = request.GET.get(
        'groupe_classe'
    )

    annee_id = request.GET.get(
        'annee_scolaire'
    )

    action = request.GET.get(
        'action'
    )

    # ========================================================
    # INSCRIPTIONS
    # ========================================================

    inscriptions = (
        EleveInscrit.objects
        .select_related(
            'eleve',
            'annee_scolaire',
            'niveau',
            'groupe_classe'
        )
        .filter(
            actif=True
        )
    )

    if niveau_id:

        inscriptions = inscriptions.filter(
            niveau_id=niveau_id
        )

    if groupe_id:

        inscriptions = inscriptions.filter(
            groupe_classe_id=groupe_id
        )

    if annee_id:

        inscriptions = inscriptions.filter(
            annee_scolaire_id=annee_id
        )

    # ========================================================
    # INFORMATIONS
    # ========================================================

    eleves_info = []

    for inscription in inscriptions:

        eleve = inscription.eleve

        frais = FraisScolarite.objects.filter(
            eleve=eleve,
            annee_scolaire=inscription.annee_scolaire
        ).first()

        montant_total = Decimal('0')
        total_paye = Decimal('0')
        montant_restant = Decimal('0')

        statut_paiement = (
            "Aucune donnée de paiement"
        )

        if frais:

            montant_total = (
                frais.montant_total
                or Decimal('0')
            )

            total_paye = (
                frais.total_paye
                or Decimal('0')
            )

            montant_restant = (
                montant_total
                - total_paye
            )

            if montant_restant < 0:

                montant_restant = Decimal('0')

            if (
                montant_total > 0
                and montant_restant == 0
            ):

                statut_paiement = (
                    "Paiement complet"
                )

            elif (
                total_paye > 0
                and montant_restant > 0
            ):

                statut_paiement = (
                    "Paiement partiel"
                )

            else:

                statut_paiement = (
                    "En attente de paiement"
                )

        # ====================================================
        # FILTRE IMPAYÉS
        # ====================================================

        if (
            action == 'impaye'
            and montant_restant <= 0
        ):

            continue

        eleves_info.append({
            'inscription': inscription,
            'eleve': eleve,

            'annee_scolaire':
                inscription.annee_scolaire,

            'niveau':
                inscription.niveau,

            'groupe_classe':
                inscription.groupe_classe,

            'frais':
                frais,

            'montant_total':
                montant_total,

            'total_paye':
                total_paye,

            'montant_restant':
                montant_restant,

            'statut_paiement':
                statut_paiement,
        })

    # ========================================================
    # TOTAL RESTANT
    # ========================================================

    total_restant = sum(
        (
            info['montant_restant']
            for info in eleves_info
            if info['montant_restant'] > 0
        ),
        Decimal('0')
    )

    # ========================================================
    # OBJETS SÉLECTIONNÉS
    # ========================================================

    niveau_obj = None

    if niveau_id:

        niveau_obj = (
            Niveau.objects
            .filter(id=niveau_id)
            .first()
        )

    groupe_obj = None

    if groupe_id:

        groupe_obj = (
            GroupeClasse.objects
            .filter(id=groupe_id)
            .first()
        )

    annee_scolaire_obj = None

    if annee_id:

        annee_scolaire_obj = (
            AnneeScolaire.objects
            .filter(id=annee_id)
            .first()
        )

    # ========================================================
    # CONTEXTE
    # ========================================================

    contexte = {
        'eleves_info': eleves_info,

        'niveaux': niveaux,
        'groupes': groupes,
        'annees_scolaires':
            annees_scolaires,

        'ecoles': ecoles,

        'total_restant':
            total_restant,

        'niveau_obj':
            niveau_obj,

        'groupe_obj':
            groupe_obj,

        'annee_scolaire_obj':
            annee_scolaire_obj,
    }

    return render(
        request,
        'eleve/statut_paiement_eleve.html',
        contexte
    )


# ============================================================
# AJAX : GROUPES D'UN NIVEAU
# ============================================================

@login_required
def get_groupe(request):

    niveau_id = request.GET.get(
        'niveau_id'
    )

    if not niveau_id:

        return JsonResponse({
            'groupes': []
        })

    groupes = (
        GroupeClasse.objects
        .filter(
            niveau_id=niveau_id
        )
        .order_by('nom')
        .values(
            'id',
            'nom'
        )
    )

    return JsonResponse({
        'groupes': list(groupes)
    })


# ============================================================
# DÉTAILS D'UN ÉLÈVE
# ============================================================

@login_required
def detail_eleve(request, pk):

    eleve_inscrit = get_object_or_404(
        EleveInscrit.objects.select_related(
            'eleve',
            'niveau',
            'groupe_classe',
            'annee_scolaire'
        ),
        id=pk
    )

    return render(
        request,
        'eleve/detail_eleve.html',
        {
            'eleve': eleve_inscrit
        }
    )



# ============================================================
# ÉLÈVES PAR NIVEAU ET ANNÉE
# ============================================================


@login_required
def liste_eleves_par_niveau_annee(request):

    # ==========================================================
    # RÉCUPÉRATION DES FILTRES
    # ==========================================================

    niveau_id = request.GET.get('niveau')
    annee_id = request.GET.get('annee_scolaire')

    niveaux = Niveau.objects.all().order_by('nom')
    annees = AnneeScolaire.objects.all().order_by('-id')


    # ==========================================================
    # AU PREMIER ACCÈS :
    # AUCUN ÉLÈVE N'EST AFFICHÉ
    #
    # L'utilisateur doit obligatoirement sélectionner :
    # - un niveau
    # - une année scolaire
    # ==========================================================

    eleves = EleveInscrit.objects.none()

    message = None


    # ==========================================================
    # VÉRIFICATION DES DEUX SÉLECTIONS
    # ==========================================================

    if niveau_id and annee_id:

        eleves = (
            EleveInscrit.objects
            .filter(
                actif=True,
                niveau_id=niveau_id,
                annee_scolaire_id=annee_id
            )
            .select_related(
                'eleve',
                'niveau',
                'groupe_classe',
                'annee_scolaire'
            )
            .order_by(
                'eleve__nom',
                'eleve__prenom'
            )
        )

    elif request.GET:

        # ======================================================
        # MESSAGE SI UNE SEULE SÉLECTION A ÉTÉ FAITE
        # ======================================================

        if not niveau_id and not annee_id:
            message = "Veuillez sélectionner un niveau et une année scolaire."

        elif not niveau_id:
            message = "Veuillez sélectionner un niveau."

        elif not annee_id:
            message = "Veuillez sélectionner une année scolaire."


    # ==========================================================
    # ENVOI AU TEMPLATE
    # ==========================================================

    return render(
        request,
        'eleve/liste_eleves_par_niveau_annee.html',
        {
            'eleves': eleves,
            'niveaux': niveaux,
            'annees': annees,
            'message': message,
        }
    )


# ============================================================
# ÉLÈVES PAR GROUPE ET ANNÉE
# ============================================================

@login_required
def liste_eleves_par_groupe(request):

    groupes = GroupeClasse.objects.all()
    annees = AnneeScolaire.objects.all()

    groupe_id = request.GET.get(
        'groupe'
    )

    annee_id = request.GET.get(
        'annee_scolaire'
    )

    inscriptions = (
        EleveInscrit.objects
        .filter(
            actif=True
        )
        .select_related(
            'eleve',
            'niveau',
            'groupe_classe',
            'annee_scolaire'
        )
    )

    if groupe_id:

        inscriptions = inscriptions.filter(
            groupe_classe_id=groupe_id
        )

    if annee_id:

        inscriptions = inscriptions.filter(
            annee_scolaire_id=annee_id
        )

    # IMPORTANT :
    # On conserve les objets EleveInscrit.
    #
    # Chaque ligne correspond donc exactement à une
    # inscription pour une année scolaire donnée.

    eleves = inscriptions

    context = {
        'eleves': eleves,
        'groupes': groupes,
        'annees': annees,
    }

    return render(
        request,
        'eleve/liste_eleves_par_groupe.html',
        context
    )



# ============================================================
# HISTORIQUE
# ============================================================

@login_required
def historique(request):

    if request.user.is_superuser:

        historiques = (
            Historique.objects
            .all()
            .order_by('-created_time')
        )

    else:

        historiques = (
            Historique.objects
            .filter(
                user=request.user
            )
            .order_by('-created_time')
        )

    return render(
        request,
        'eleve/historique.html',
        {
            'historiques': historiques
        }
    )


# ============================================================
# PROFIL
# ============================================================

@login_required
def profiles(request):

    user = request.user

    if request.method == "POST":

        user.nom = request.POST.get(
            "nom",
            getattr(user, 'nom', '')
        )

        user.prenom = request.POST.get(
            "prenom",
            getattr(user, 'prenom', '')
        )

        user.email = request.POST.get(
            "email",
            user.email
        )

        if hasattr(user, 'genre'):

            user.genre = request.POST.get(
                "sexe",
                user.genre
            )

        if hasattr(user, 'telephone'):

            user.telephone = request.POST.get(
                "contact",
                user.telephone
            )

        if hasattr(user, 'lieu_naiss'):

            user.lieu_naiss = request.POST.get(
                "filiation",
                user.lieu_naiss
            )

        username = request.POST.get(
            "username"
        )

        if username:

            user.username = username

        # ====================================================
        # DATE
        # ====================================================

        date_str = request.POST.get(
            "date"
        )

        if date_str:

            try:

                user.date_naissance = datetime.strptime(
                    date_str,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                messages.error(
                    request,
                    "Format de date invalide. Utilise AAAA-MM-JJ."
                )

                return redirect(
                    "profiles"
                )

        # ====================================================
        # PHOTO
        # ====================================================

        if "photo" in request.FILES:

            user.photo = request.FILES[
                "photo"
            ]

        # ====================================================
        # SAUVEGARDE
        # ====================================================

        try:

            user.save()

            messages.success(
                request,
                "Votre profil a été mis à jour avec succès."
            )

        except Exception as e:

            messages.error(
                request,
                f"Erreur lors de la sauvegarde : {e}"
            )

        return redirect(
            "profiles"
        )

    return render(
        request,
        'eleve/profil.html',
        {
            'user': user
        }
    )


# ============================================================
# DROITS DU FONDATEUR
# ============================================================


# ============================================================
# STATUT DES PAIEMENTS - FONDATEUR
# ============================================================

@login_required
def statut_paiement_eleve_fondateur(request):

    niveaux = Niveau.objects.all()
    groupes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    niveau_id = request.GET.get(
        'niveau'
    )

    groupe_id = request.GET.get(
        'groupe_classe'
    )

    annee_id = request.GET.get(
        'annee_scolaire'
    )

    inscriptions = (
        EleveInscrit.objects
        .filter(
            actif=True
        )
        .select_related(
            'eleve',
            'niveau',
            'groupe_classe',
            'annee_scolaire'
        )
    )

    if niveau_id:

        inscriptions = inscriptions.filter(
            niveau_id=niveau_id
        )

    if groupe_id:

        inscriptions = inscriptions.filter(
            groupe_classe_id=groupe_id
        )

    if annee_id:

        inscriptions = inscriptions.filter(
            annee_scolaire_id=annee_id
        )

    eleves_info = []

    for inscription in inscriptions:

        eleve = inscription.eleve

        frais_scolarite = (
            FraisScolarite.objects
            .filter(
                eleve=eleve,
                annee_scolaire=inscription.annee_scolaire
            )
            .first()
        )

        if frais_scolarite:

            montant_total = (
                frais_scolarite.montant_total
                or Decimal('0')
            )

            total_paye = (
                frais_scolarite.total_paye
                or Decimal('0')
            )

            solde = (
                montant_total
                - total_paye
            )

            if solde < 0:

                solde = Decimal('0')

            if (
                montant_total > 0
                and solde == 0
            ):

                statut_paiement = (
                    'Paiement complet'
                )

            elif total_paye > 0:

                statut_paiement = (
                    'Paiement partiel'
                )

            else:

                statut_paiement = (
                    'En attente de paiement'
                )

        else:

            montant_total = Decimal('0')
            total_paye = Decimal('0')
            solde = Decimal('0')

            statut_paiement = (
                'Aucune donnée de paiement'
            )

        eleves_info.append({
            'inscription':
                inscription,

            'eleve':
                eleve,

            'frais':
                frais_scolarite,

            'montant_total':
                montant_total,

            'total_paye':
                total_paye,

            'solde':
                solde,

            'statut_paiement':
                statut_paiement,
        })

    return render(
        request,
        'admin/statut_paiement_eleve.html',
        {
            'eleves_info':
                eleves_info,

            'niveaux':
                niveaux,

            'groupes':
                groupes,

            'annees_scolaires':
                annees_scolaires,
        }
    )


# ============================================================
# DÉTAIL ÉLÈVE - FONDATEUR
# ============================================================

@login_required
def detail_eleves(request, pk):

    eleve = get_object_or_404(
        Eleve,
        id=pk
    )

    return render(
        request,
        'admin/detail_eleve.html',
        {
            'eleve': eleve
        }
    )


# ============================================================
# ÉLÈVES PAR NIVEAU - FONDATEUR
# ============================================================

@login_required
def liste_eleves_niveau(request):

    niveau_id = request.GET.get(
        'niveau'
    )

    annee_id = request.GET.get(
        'annee_scolaire'
    )

    niveaux = Niveau.objects.all()
    annees = AnneeScolaire.objects.all()

    inscriptions = (
        EleveInscrit.objects
        .filter(
            actif=True
        )
        .select_related(
            'eleve',
            'niveau',
            'groupe_classe',
            'annee_scolaire'
        )
    )

    if niveau_id:

        inscriptions = inscriptions.filter(
            niveau_id=niveau_id
        )

    if annee_id:

        inscriptions = inscriptions.filter(
            annee_scolaire_id=annee_id
        )

    eleves = [
        inscription.eleve
        for inscription in inscriptions
    ]

    return render(
        request,
        'eleve/liste_eleves_par_niveau_annee.html',
        {
            'eleves': eleves,
            'niveaux': niveaux,
            'annees': annees,
        }
    )


# ============================================================
# ÉLÈVES PAR CLASSE - FONDATEUR
# ============================================================

@login_required
def liste_eleves_par_classe(request):

    groupes = GroupeClasse.objects.all()
    annees = AnneeScolaire.objects.all()

    groupe_id = request.GET.get(
        'groupe'
    )

    annee_id = request.GET.get(
        'annee_scolaire'
    )

    inscriptions = (
        EleveInscrit.objects
        .filter(
            actif=True
        )
        .select_related(
            'eleve',
            'niveau',
            'groupe_classe',
            'annee_scolaire'
        )
    )

    if groupe_id:

        inscriptions = inscriptions.filter(
            groupe_classe_id=groupe_id
        )

    if annee_id:

        inscriptions = inscriptions.filter(
            annee_scolaire_id=annee_id
        )

    eleves = [
        inscription.eleve
        for inscription in inscriptions
    ]

    context = {
        'eleves': eleves,
        'groupes': groupes,
        'annees': annees
    }

    return render(
        request,
        'admin/liste_eleves_par_groupe.html',
        context
    )


# ============================================================
# RÉINSCRIPTION
# ============================================================

@login_required
def reinscription_eleve(request):

    eleves = (
        Eleve.objects
        .filter(
            actif=True
        )
        .order_by(
            'nom',
            'prenom'
        )
    )

    niveaux = Niveau.objects.all().order_by('nom')
    groupes = GroupeClasse.objects.all().order_by('nom')
    annees = AnneeScolaire.objects.all().order_by('-id')

    if request.method == "POST":

        matricule = request.POST.get(
            "matricule",
            ""
        ).strip()

        niveau_id = request.POST.get(
            "niveau"
        )

        groupe_id = request.POST.get(
            "groupe"
        )

        annee_id = request.POST.get(
            "annee"
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        if (
            not matricule
            or not niveau_id
            or not groupe_id
            or not annee_id
        ):

            messages.error(
                request,
                "Tous les champs sont obligatoires."
            )

            return redirect(
                "reinscrire_eleve"
            )

        # ====================================================
        # ÉLÈVE
        # ====================================================

        eleve = (
            Eleve.objects
            .filter(
                matricule__iexact=matricule
            )
            .first()
        )

        if not eleve:

            messages.error(
                request,
                "Aucun élève trouvé avec ce matricule."
            )

            return redirect(
                "reinscrire_eleve"
            )

        # ====================================================
        # OBJETS
        # ====================================================

        niveau = get_object_or_404(
            Niveau,
            id=niveau_id
        )

        groupe = get_object_or_404(
            GroupeClasse,
            id=groupe_id
        )

        annee = get_object_or_404(
            AnneeScolaire,
            id=annee_id
        )

        # ====================================================
        # COHÉRENCE NIVEAU / CLASSE
        # ====================================================

        if groupe.niveau_id != niveau.id:

            messages.error(
                request,
                "La classe sélectionnée ne correspond pas au niveau."
            )

            return redirect(
                "reinscrire_eleve"
            )

        # ====================================================
        # INSCRIPTION
        # ====================================================

        inscription, created = (
            EleveInscrit.objects
            .get_or_create(
                eleve=eleve,
                annee_scolaire=annee,
                defaults={
                    "niveau": niveau,
                    "groupe_classe": groupe,
                    "actif": True,
                }
            )
        )

        if not created:

            inscription.niveau = niveau
            inscription.groupe_classe = groupe
            inscription.actif = True

            inscription.save()

            message = (
                f"{eleve.nom} {eleve.prenom} "
                f"a été réinscrit pour {annee.nom} "
                f"(inscription mise à jour)."
            )

        else:

            message = (
                f"{eleve.nom} {eleve.prenom} "
                f"a été réinscrit avec succès "
                f"pour {annee.nom}."
            )

        # ====================================================
        # MAINTENIR LES CHAMPS LEGACY ELEVE
        # ====================================================

        eleve.niveau = niveau
        eleve.groupe_classe = groupe
        eleve.annee_scolaire = annee

        eleve.save()

        # ====================================================
        # FRAIS
        # ====================================================

        montant_total = (
            niveau.montant_frais
            or Decimal('0')
        )

        FraisScolarite.objects.get_or_create(
            eleve=eleve,
            annee_scolaire=annee,
            defaults={
                "montant_total":
                    montant_total,

                "tranche1":
                    Decimal('0'),

                "tranche2":
                    Decimal('0'),

                "tranche3":
                    Decimal('0'),

                "total_paye":
                    Decimal('0'),

                "solde":
                    montant_total,

                "est_paye":
                    False,
            }
        )

        # ====================================================
        # HISTORIQUE
        # ====================================================

        Historique.objects.create(
            user=request.user,
            action=(
                f"A réinscrit l'élève "
                f"{eleve.prenom} {eleve.nom} "
                f"en {niveau.nom} "
                f"pour l'année {annee.nom}"
            )
        )

        messages.success(
            request,
            message
        )

        return redirect(
            "reinscrire_eleve"
        )

    return render(
        request,
        "eleve/reinscription.html",
        {
            "eleves": eleves,
            "niveaux": niveaux,
            "groupes": groupes,
            "annees": annees
        }
    )


# ============================================================
# AJAX : INFORMATIONS D'UN ÉLÈVE
# ============================================================

@login_required
def get_eleve_info(request):

    matricule = request.GET.get(
        'matricule',
        ''
    ).strip()

    contact_pere = request.GET.get(
        'contact_pere',
        ''
    ).strip()

    eleve_id = request.GET.get(
        'id',
        ''
    ).strip()

    # ========================================================
    # CONSTRUCTION DES DONNÉES
    # ========================================================

    def construire_donnees(
        eleve,
        inscription=None
    ):

        # ----------------------------------------------------
        # Si une inscription existe,
        # elle est prioritaire pour les données scolaires.
        # ----------------------------------------------------

        if inscription:

            annee_id = (
                inscription.annee_scolaire_id
                or ''
            )

            niveau_id = (
                inscription.niveau_id
                or ''
            )

            groupe_id = (
                inscription.groupe_classe_id
                or ''
            )

        else:

            annee_id = (
                eleve.annee_scolaire_id
                or ''
            )

            niveau_id = (
                eleve.niveau_id
                or ''
            )

            groupe_id = (
                eleve.groupe_classe_id
                or ''
            )

        # ----------------------------------------------------
        # DONNÉES
        # ----------------------------------------------------

        return {
            'success': True,

            'id':
                eleve.id,

            'matricule':
                eleve.matricule or '',

            'nom':
                eleve.nom or '',

            'prenom':
                eleve.prenom or '',

            'date_naissance': (
                eleve.date_naissance.strftime(
                    '%Y-%m-%d'
                )
                if eleve.date_naissance
                else ''
            ),

            'lieu_naissance':
                eleve.lieu_naissance or '',

            'sexe':
                eleve.genre or '',

            'contact':
                eleve.telephone or '',

            'pere':
                eleve.pere or '',

            'fp':
                eleve.profession_pere or '',

            'cp':
                eleve.contact_parent or '',

            'mere':
                eleve.mere or '',

            'fm':
                eleve.profession_mere or '',

            'cm':
                eleve.contact_mere or '',

            'photo_url': (
                eleve.photo.url
                if eleve.photo
                else ''
            ),

            'annee_id':
                annee_id,

            'niveau_id':
                niveau_id,

            'groupe_id':
                groupe_id,
        }

    # ========================================================
    # RECHERCHE PAR ID
    # ========================================================

    if eleve_id:

        try:

            eleve = get_object_or_404(
                Eleve,
                id=eleve_id
            )

            inscription = (
                EleveInscrit.objects
                .select_related(
                    'niveau',
                    'groupe_classe',
                    'annee_scolaire'
                )
                .filter(
                    eleve=eleve,
                    actif=True
                )
                .order_by(
                    '-annee_scolaire_id'
                )
                .first()
            )

            return JsonResponse(
                construire_donnees(
                    eleve,
                    inscription
                )
            )

        except Exception:

            return JsonResponse({
                'success': False,
                'error':
                    'Élève introuvable.'
            })

    # ========================================================
    # RECHERCHE PAR MATRICULE
    # ========================================================

    if matricule:

        eleve = (
            Eleve.objects
            .filter(
                matricule__iexact=matricule
            )
            .first()
        )

        if not eleve:

            return JsonResponse({
                'success': False,
                'error':
                    'Élève introuvable avec ce matricule.'
            })

        inscription = (
            EleveInscrit.objects
            .select_related(
                'niveau',
                'groupe_classe',
                'annee_scolaire'
            )
            .filter(
                eleve=eleve,
                actif=True
            )
            .order_by(
                '-annee_scolaire_id'
            )
            .first()
        )

        data = construire_donnees(
            eleve,
            inscription
        )

        data['type'] = 'matricule'

        return JsonResponse(
            data
        )

    # ========================================================
    # RECHERCHE PAR CONTACT DU PÈRE
    # ========================================================

    if contact_pere:

        eleves = (
            Eleve.objects
            .filter(
                contact_parent__iexact=contact_pere
            )
            .order_by(
                'nom',
                'prenom'
            )
        )

        if not eleves.exists():

            return JsonResponse({
                'success': False,
                'error':
                    "Aucun élève trouvé avec ce contact du père."
            })

        # ----------------------------------------------------
        # UN SEUL ENFANT
        # ----------------------------------------------------

        if eleves.count() == 1:

            eleve = eleves.first()

            inscription = (
                EleveInscrit.objects
                .select_related(
                    'niveau',
                    'groupe_classe',
                    'annee_scolaire'
                )
                .filter(
                    eleve=eleve,
                    actif=True
                )
                .order_by(
                    '-annee_scolaire_id'
                )
                .first()
            )

            data = construire_donnees(
                eleve,
                inscription
            )

            data['type'] = 'contact_pere'

            return JsonResponse(
                data
            )

        # ----------------------------------------------------
        # PLUSIEURS ENFANTS
        # ----------------------------------------------------

        liste_eleves = []

        for eleve in eleves:

            liste_eleves.append({
                'id':
                    eleve.id,

                'matricule':
                    eleve.matricule or '',

                'nom':
                    eleve.nom or '',

                'prenom':
                    eleve.prenom or '',

                'sexe':
                    eleve.genre or '',

                'date_naissance': (
                    eleve.date_naissance.strftime(
                        '%Y-%m-%d'
                    )
                    if eleve.date_naissance
                    else ''
                ),
            })

        return JsonResponse({
            'success':
                True,

            'type':
                'plusieurs_eleves',

            'eleves':
                liste_eleves
        })

    # ========================================================
    # AUCUNE RECHERCHE
    # ========================================================

    return JsonResponse({
        'success':
            False,

        'error':
            'Veuillez saisir le matricule ou le contact du père.'
    })


# ============================================================
# GÉNÉRATION D'UN MATRICULE
# ============================================================

def generer_matricule(eleve):

    # ========================================================
    # NOM
    # ========================================================

    nom = (
        eleve.nom
        or ''
    ).strip().upper()

    nom = re.sub(
        r'[^A-Z]',
        '',
        nom
    )

    nom_code = (
        nom[:2]
        if len(nom) >= 2
        else nom.ljust(2, 'X')
    )

    # ========================================================
    # PRÉNOM
    # ========================================================

    prenom = (
        eleve.prenom
        or ''
    ).strip().upper()

    prenom = re.sub(
        r'[^A-Z]',
        '',
        prenom
    )

    prenom_code = (
        prenom[:2]
        if len(prenom) >= 2
        else prenom.ljust(2, 'X')
    )

    # ========================================================
    # ANNÉE
    # ========================================================

    if eleve.date_naissance:

        annee_naissance = str(
            eleve.date_naissance.year
        )

    else:

        annee_naissance = '0000'

    # ========================================================
    # PRÉFIXE
    # ========================================================

    prefixe = (
        nom_code
        + prenom_code
        + annee_naissance
    )

    # ========================================================
    # NUMÉRO
    # ========================================================

    for numero in range(1, 100):

        suffixe = f"{numero:02d}"

        matricule = (
            prefixe
            + suffixe
        )

        if not Eleve.objects.filter(
            matricule=matricule
        ).exists():

            return matricule

    raise ValueError(
        "Impossible de générer un matricule unique."
    )



# ============================================================
# GESTION DES BADGES ÉLÈVES
# ============================================================

@login_required
def gestion_badges_eleves(request):

    etablissement = (
        Etablissement.objects
        .first()
    )

    recherche = request.GET.get(
        'recherche',
        ''
    ).strip()

    annee_id = request.GET.get(
        'annee',
        ''
    ).strip()

    niveau_id = request.GET.get(
        'niveau',
        ''
    ).strip()

    groupe_id = request.GET.get(
        'groupe',
        ''
    ).strip()


    # ========================================================
    # AUCUN ÉLÈVE PAR DÉFAUT
    # ========================================================

    eleves = (
        EleveInscrit.objects
        .none()
    )


    # ========================================================
    # CONSTRUCTION DU FILTRE
    # ========================================================

    filtres = {
        'actif': True
    }


    # ========================================================
    # FILTRE ANNÉE
    # ========================================================

    if annee_id:

        filtres['annee_scolaire_id'] = annee_id


    # ========================================================
    # FILTRE NIVEAU
    # ========================================================

    if niveau_id:

        filtres['niveau_id'] = niveau_id


    # ========================================================
    # FILTRE CLASSE
    # ========================================================

    if groupe_id:

        filtres['groupe_classe_id'] = groupe_id


    # ========================================================
    # RECHERCHE NOM / PRÉNOM / MATRICULE
    # ========================================================

    recherche_filter = None

    if recherche:

        recherche_filter = (
            Q(
                eleve__nom__icontains=recherche
            )
            |
            Q(
                eleve__prenom__icontains=recherche
            )
            |
            Q(
                eleve__matricule__icontains=recherche
            )
        )


    # ========================================================
    # EXÉCUTER LA RECHERCHE
    # ========================================================

    if (
        recherche
        or annee_id
        or niveau_id
        or groupe_id
    ):

        eleves = (
            EleveInscrit.objects
            .filter(**filtres)
        )

        if recherche_filter:

            eleves = eleves.filter(
                recherche_filter
            )

        eleves = (
            eleves
            .select_related(
                'eleve',
                'niveau',
                'groupe_classe',
                'annee_scolaire'
            )
            .order_by(
                'eleve__nom',
                'eleve__prenom'
            )
        )


    # ========================================================
    # ANNÉES SCOLAIRES
    # ========================================================

    annees = (
        EleveInscrit.objects
        .filter(
            annee_scolaire__isnull=False
        )
        .values(
            'annee_scolaire_id',
            'annee_scolaire__nom'
        )
        .distinct()
        .order_by(
            '-annee_scolaire_id'
        )
    )


    # ========================================================
    # NIVEAUX
    # ========================================================

    niveaux = (
        EleveInscrit.objects
        .filter(
            niveau__isnull=False
        )
        .values(
            'niveau_id',
            'niveau__nom'
        )
        .distinct()
        .order_by(
            'niveau__nom'
        )
    )


    # ========================================================
    # GROUPES / CLASSES
    # ========================================================

    groupes = (
        EleveInscrit.objects
        .filter(
            groupe_classe__isnull=False
        )
        .values(
            'groupe_classe_id',
            'groupe_classe__nom'
        )
        .distinct()
        .order_by(
            'groupe_classe__nom'
        )
    )


    # ========================================================
    # CONTEXTE
    # ========================================================

    context = {

        'etablissement':
            etablissement,

        'eleves':
            eleves,

        'annees':
            annees,

        'niveaux':
            niveaux,

        'groupes':
            groupes,

        'recherche':
            recherche,

        'annee_selectionnee':
            annee_id,

        'niveau_selectionne':
            niveau_id,

        'groupe_selectionne':
            groupe_id,
    }


    return render(
        request,
        'eleve/gestion_badges_eleves.html',
        context
    )


# ============================================================
# BADGE D'UN ÉLÈVE
# ============================================================

@login_required
def badge_eleve(request, eleve_id):

    eleve = get_object_or_404(
        EleveInscrit.objects.select_related(
            'eleve',
            'niveau',
            'groupe_classe',
            'annee_scolaire'
        ),
        id=eleve_id
    )

    etablissement = (
        Etablissement.objects
        .first()
    )

    context = {
        'eleve':
            eleve,

        'etablissement':
            etablissement,
    }

    return render(
        request,
        'eleve/badge_eleve.html',
        context
    )


# ============================================================
# IMPRESSION DE PLUSIEURS BADGES
# ============================================================

@login_required
def badges_eleves_impression(request):

    if request.method != 'POST':

        return redirect(
            'gestion_badges_eleves'
        )

    eleves_ids = request.POST.getlist(
        'eleves'
    )

    eleves_ids = [
        identifiant
        for identifiant in eleves_ids
        if identifiant
    ]

    if not eleves_ids:

        messages.warning(
            request,
            "Veuillez sélectionner au moins un élève."
        )

        return redirect(
            'gestion_badges_eleves'
        )

    eleves = (
        EleveInscrit.objects
        .filter(
            id__in=eleves_ids,
            actif=True
        )
        .select_related(
            'eleve',
            'niveau',
            'groupe_classe',
            'annee_scolaire'
        )
        .order_by(
            'eleve__nom',
            'eleve__prenom'
        )
    )

    if not eleves.exists():

        messages.error(
            request,
            "Aucune inscription élève correspondante."
        )

        return redirect(
            'gestion_badges_eleves'
        )

    etablissement = (
        Etablissement.objects
        .first()
    )

    context = {
        'eleves':
            eleves,

        'etablissement':
            etablissement,

        'nombre_eleves':
            eleves.count(),
    }

    return render(
        request,
        'eleve/impression_badges_eleves.html',
        context
    )


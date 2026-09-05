from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from matiere.models import Matiere, EnseignantMatiere
from eleve.models import EleveInscrit
from annee_scolaire.models import AnneeScolaire
from note.models import Note
from groupe_classe.models import GroupeClasse
from niveau.models import Niveau
from enseignant.models import Enseignant

# ============================================================
# AFFICHER LES NOTES
# ============================================================

def note(request):

    matieres = Matiere.objects.all()

    notes = Note.objects.select_related(
        'eleve',
        'inscription',
        'matiere',
        'annee_scolaire'
    ).all()

    annees = AnneeScolaire.objects.all()

    eleves = EleveInscrit.objects.select_related(
        'eleve',
        'niveau',
        'groupe_classe',
        'annee_scolaire'
    ).all()

    context = {
        'matieres': matieres,
        'notes': notes,
        'annes': annees,
        'eleves': eleves,
    }

    return render(
        request,
        'note/note.html',
        context
    )


# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect

# from enseignant.models import Enseignant
# from matiere.models import Matiere, EnseignantMatiere
# from niveau.models import Niveau
# from groupe_classe.models import GroupeClasse
# from annee_scolaire.models import AnneeScolaire

# from eleve.models import EleveInscrit
# from note.models import Note

@login_required
def modifier_notes(request):
    # ============================================================
    # 1. RÉCUPÉRER L'ENSEIGNANT CONNECTÉ
    # ============================================================
    try:
        enseignant = request.user.enseignant_profile
    except Enseignant.DoesNotExist:
        messages.error(
            request,
            "Aucun profil enseignant n'est associé à votre compte."
        )
        return render(
            request,
            "note/modifier_notes.html"
        )

    # ============================================================
    # 2. RÉCUPÉRER UNIQUEMENT LES AFFECTATIONS DE L'ENSEIGNANT
    # ============================================================
    affectations = (
        EnseignantMatiere.objects
        .filter(enseignant=enseignant)
        .select_related(
            "matiere",
            "niveau",
            "groupe_classe"
        )
    )

    # ============================================================
    # 3. RÉCUPÉRER LES FILTRES
    # ============================================================
    annee_id = (
        request.POST.get("annee")
        or request.GET.get("annee")
    )

    niveau_id = (
        request.POST.get("niveau")
        or request.GET.get("niveau")
    )

    groupe_id = (
        request.POST.get("groupe")
        or request.GET.get("groupe")
    )

    matiere_id = (
        request.POST.get("matiere")
        or request.GET.get("matiere")
    )

    trimestre = (
        request.POST.get("trimestre")
        or request.GET.get("trimestre")
    )

    # ============================================================
    # 4. URL DE RETOUR
    # ============================================================
    url_retour = (
        f"{request.path}"
        f"?annee={annee_id or ''}"
        f"&niveau={niveau_id or ''}"
        f"&groupe={groupe_id or ''}"
        f"&matiere={matiere_id or ''}"
        f"&trimestre={trimestre or ''}"
    )

    # ============================================================
    # 5. MODIFICATION D'UNE NOTE
    # ============================================================
    if request.method == "POST":

        inscription_id = request.POST.get("inscription_id")
        note_id = request.POST.get("note_id")

        note_cours = request.POST.get("note_cours")
        note_comp = request.POST.get("note_comp")

        # --------------------------------------------------------
        # Vérification des identifiants
        # --------------------------------------------------------
        if not inscription_id or not note_id:
            messages.error(
                request,
                "Les informations nécessaires à la modification "
                "de la note sont incomplètes."
            )
            return redirect(url_retour)

        # --------------------------------------------------------
        # Vérification des critères
        # --------------------------------------------------------
        if not all([
            annee_id,
            niveau_id,
            groupe_id,
            matiere_id,
            trimestre
        ]):
            messages.error(
                request,
                "Les critères de recherche sont incomplets."
            )
            return redirect(url_retour)

        # ========================================================
        # 6. VÉRIFICATION DE L'AUTORISATION DE L'ENSEIGNANT
        # ========================================================
        affectation = (
            affectations
            .filter(
                matiere_id=matiere_id,
                niveau_id=niveau_id,
                groupe_classe_id=groupe_id
            )
            .first()
        )

        if not affectation:
            messages.error(
                request,
                "Vous n'êtes pas autorisé à modifier les notes "
                "de cette matière dans cette classe."
            )
            return redirect(url_retour)

        # ========================================================
        # 7. RÉCUPÉRER L'INSCRIPTION
        # ========================================================
        try:
            inscription = (
                EleveInscrit.objects
                .select_related("eleve")
                .get(
                    id=inscription_id,
                    annee_scolaire_id=annee_id,
                    niveau_id=niveau_id,
                    groupe_classe_id=groupe_id,
                    actif=True
                )
            )

        except EleveInscrit.DoesNotExist:
            messages.error(
                request,
                "L'inscription de l'élève est introuvable "
                "ou ne correspond pas aux critères sélectionnés."
            )
            return redirect(url_retour)

        # --------------------------------------------------------
        # IMPORTANT :
        # Note.eleve attend une instance de Eleve.
        # --------------------------------------------------------
        eleve = inscription.eleve

        # ========================================================
        # 8. RÉCUPÉRER LA NOTE
        # ========================================================
        try:
            note = (
                Note.objects
                .select_related(
                    "eleve",
                    "inscription",
                    "matiere",
                    "annee_scolaire"
                )
                .get(
                    id=note_id,
                    eleve=eleve,
                    inscription=inscription,
                    matiere_id=matiere_id,
                    trimestre=trimestre,
                    annee_scolaire_id=annee_id
                )
            )

        except Note.DoesNotExist:
            messages.error(
                request,
                "La note sélectionnée est introuvable "
                "ou ne correspond pas aux critères sélectionnés."
            )
            return redirect(url_retour)

        # ========================================================
        # 9. CONVERSION DES NOTES
        # ========================================================
        try:

            # ------------------------------
            # Note de cours
            # ------------------------------
            if note_cours is None or note_cours.strip() == "":
                note.note_cours = None
            else:
                note.note_cours = float(
                    note_cours.replace(",", ".")
                )

            # ------------------------------
            # Note de composition
            # ------------------------------
            if note_comp is None or note_comp.strip() == "":
                note.note_comp = None
            else:
                note.note_comp = float(
                    note_comp.replace(",", ".")
                )

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            messages.error(
                request,
                "Les notes saisies doivent être des nombres valides."
            )
            return redirect(url_retour)

        # ========================================================
        # 10. VÉRIFICATION DES VALEURS
        # ========================================================

        if (
            note.note_cours is not None
            and not 0 <= note.note_cours <= 20
        ):
            messages.error(
                request,
                "La note de cours doit être comprise entre 0 et 20."
            )
            return redirect(url_retour)

        if (
            note.note_comp is not None
            and not 0 <= note.note_comp <= 20
        ):
            messages.error(
                request,
                "La note de composition doit être comprise entre 0 et 20."
            )
            return redirect(url_retour)

        # ========================================================
        # 11. ENREGISTRER
        # ========================================================
        note.save()

        messages.success(
            request,
            f"Les notes de {eleve.nom} {eleve.prenom} "
            f"ont été modifiées avec succès."
        )

        return redirect(url_retour)

    # ============================================================
    # 12. ANNÉES SCOLAIRES
    # ============================================================
    annees = (
        AnneeScolaire.objects
        .all()
        .order_by("-nom")
    )

    # ============================================================
    # 13. NIVEAUX
    # UNIQUEMENT CEUX DE L'ENSEIGNANT
    # ============================================================
    niveaux = (
        affectations
        .values(
            "niveau_id",
            "niveau__nom"
        )
        .distinct()
        .order_by("niveau__nom")
    )

    # ============================================================
    # 14. CLASSES
    # UNIQUEMENT LES CLASSES DE L'ENSEIGNANT
    # ============================================================
    groupes_queryset = affectations

    if niveau_id:
        groupes_queryset = groupes_queryset.filter(
            niveau_id=niveau_id
        )

    groupes = (
        groupes_queryset
        .values(
            "groupe_classe_id",
            "groupe_classe__nom"
        )
        .distinct()
        .order_by("groupe_classe__nom")
    )

    # ============================================================
    # 15. MATIÈRES
    #
    # C'EST LA PARTIE IMPORTANTE :
    #
    # On part de "affectations", donc uniquement des matières
    # affectées à l'enseignant connecté.
    #
    # Puis on filtre selon le niveau et la classe sélectionnés.
    # ============================================================
    matieres_queryset = affectations

    if niveau_id:
        matieres_queryset = matieres_queryset.filter(
            niveau_id=niveau_id
        )

    if groupe_id:
        matieres_queryset = matieres_queryset.filter(
            groupe_classe_id=groupe_id
        )

    matieres = (
        matieres_queryset
        .values(
            "matiere_id",
            "matiere__nom"
        )
        .distinct()
        .order_by("matiere__nom")
    )

    # ============================================================
    # 16. LISTE DES ÉLÈVES ET NOTES
    # ============================================================
    eleves_notes = []

    if all([
        annee_id,
        niveau_id,
        groupe_id,
        matiere_id,
        trimestre
    ]):

        # --------------------------------------------------------
        # Vérification supplémentaire de l'autorisation
        # --------------------------------------------------------
        autorisation = (
            affectations
            .filter(
                matiere_id=matiere_id,
                niveau_id=niveau_id,
                groupe_classe_id=groupe_id
            )
            .exists()
        )

        if not autorisation:

            messages.error(
                request,
                "Vous n'êtes pas autorisé à gérer cette "
                "matière dans cette classe."
            )

        else:

            # ----------------------------------------------------
            # Récupérer les inscriptions de l'année/classe
            # ----------------------------------------------------
            inscriptions = (
                EleveInscrit.objects
                .filter(
                    annee_scolaire_id=annee_id,
                    niveau_id=niveau_id,
                    groupe_classe_id=groupe_id,
                    actif=True
                )
                .select_related("eleve")
                .order_by(
                    "eleve__nom",
                    "eleve__prenom"
                )
            )

            # ----------------------------------------------------
            # Récupérer les notes
            # ----------------------------------------------------
            for inscription in inscriptions:

                note = (
                    Note.objects
                    .filter(
                        eleve=inscription.eleve,
                        inscription=inscription,
                        matiere_id=matiere_id,
                        trimestre=trimestre,
                        annee_scolaire_id=annee_id
                    )
                    .first()
                )

                eleves_notes.append({
                    "inscription": inscription,
                    "eleve": inscription.eleve,
                    "note": note,
                })

    # ============================================================
    # 17. CONTEXTE
    # ============================================================
    context = {
        "enseignant": enseignant,

        "annees": annees,
        "niveaux": niveaux,
        "groupes": groupes,
        "matieres": matieres,

        "eleves_notes": eleves_notes,

        "annee_selectionnee": annee_id,
        "niveau_selectionne": niveau_id,
        "groupe_selectionne": groupe_id,
        "matiere_selectionnee": matiere_id,
        "trimestre_selectionne": trimestre,
    }

    # ============================================================
    # 18. AFFICHER LA PAGE
    # ============================================================
    return render(
        request,
        "note/modifier_notes.html",
        context
    )





# ============================================================
# SUPPRESSION D'UNE NOTE
# ============================================================

def supprimer(request, pk):

    note_obj = get_object_or_404(
        Note,
        id=pk
    )

    note_obj.delete()

    messages.success(
        request,
        "La note a été supprimée avec succès."
    )

    return redirect('note')


# ============================================================
# ATTRIBUTION DES NOTES
# ADMINISTRATION
# ============================================================

def attribuer_notes(request):

    niveaux = Niveau.objects.all()
    groupes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()
    matieres = Matiere.objects.all()

    niveau_id = request.GET.get('niveau')
    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')

    eleves = None

    # --------------------------------------------------------
    # FILTRAGE DES ÉLÈVES
    # --------------------------------------------------------

    try:

        if niveau_id and groupe_id and annee_id:

            niveau_id = int(niveau_id)
            groupe_id = int(groupe_id)
            annee_id = int(annee_id)

            eleves = EleveInscrit.objects.filter(
                niveau_id=niveau_id,
                groupe_classe_id=groupe_id,
                annee_scolaire_id=annee_id,
                actif=True
            ).select_related(
                'eleve',
                'niveau',
                'groupe_classe',
                'annee_scolaire'
            )

    except (ValueError, TypeError):

        eleves = None

    # --------------------------------------------------------
    # ENREGISTREMENT D'UNE NOTE
    # --------------------------------------------------------

    if request.method == 'POST':

        # IMPORTANT :
        # "eleve" contient maintenant l'ID de EleveInscrit

        inscription_id = request.POST.get('eleve')

        # Accepte les deux noms possibles
        annee_id_post = (
            request.POST.get('anne')
            or request.POST.get('annee_scolaire')
        )

        matiere_id = request.POST.get('mat')
        trimestre = request.POST.get('trimestre')
        note_cours_value = request.POST.get('nc')
        note_comp_value = request.POST.get('nco')

        # ----------------------------------------------------
        # Vérification des champs
        # ----------------------------------------------------

        if not all([
            inscription_id,
            annee_id_post,
            matiere_id,
            trimestre,
            note_cours_value,
            note_comp_value
        ]):

            message = "Veuillez remplir tous les champs."

            if request.headers.get(
                'x-requested-with'
            ) == 'XMLHttpRequest':

                return JsonResponse(
                    {'error': message},
                    status=400
                )

            messages.error(
                request,
                message
            )

        else:

            try:

                # ------------------------------------------------
                # Récupération de l'inscription
                # ------------------------------------------------

                inscription = EleveInscrit.objects.select_related(
                    'eleve',
                    'niveau',
                    'groupe_classe',
                    'annee_scolaire'
                ).get(
                    id=inscription_id
                )

                # ------------------------------------------------
                # Récupération année
                # ------------------------------------------------

                annee = AnneeScolaire.objects.get(
                    id=annee_id_post
                )

                # ------------------------------------------------
                # Récupération matière
                # ------------------------------------------------

                matiere = Matiere.objects.get(
                    id=matiere_id
                )

                # ------------------------------------------------
                # Conversion
                # ------------------------------------------------

                trimestre = int(trimestre)

                note_cours = float(
                    note_cours_value
                )

                note_comp = float(
                    note_comp_value
                )

            except (
                EleveInscrit.DoesNotExist,
                AnneeScolaire.DoesNotExist,
                Matiere.DoesNotExist,
                ValueError,
                TypeError
            ):

                message = "Les données fournies sont invalides."

                if request.headers.get(
                    'x-requested-with'
                ) == 'XMLHttpRequest':

                    return JsonResponse(
                        {'error': message},
                        status=400
                    )

                messages.error(
                    request,
                    message
                )

            else:

                # ------------------------------------------------
                # Vérifier année inscription
                # ------------------------------------------------

                if inscription.annee_scolaire_id != annee.id:

                    message = (
                        "L'élève n'est pas inscrit "
                        "dans cette année scolaire."
                    )

                    if request.headers.get(
                        'x-requested-with'
                    ) == 'XMLHttpRequest':

                        return JsonResponse(
                            {'error': message},
                            status=400
                        )

                    messages.error(
                        request,
                        message
                    )

                # ------------------------------------------------
                # Vérifier note existante
                # ------------------------------------------------

                elif Note.objects.filter(
                    inscription=inscription,
                    matiere=matiere,
                    annee_scolaire=annee,
                    trimestre=trimestre
                ).exists():

                    message = (
                        "Cet élève est déjà noté dans "
                        "cette matière pour ce trimestre."
                    )

                    if request.headers.get(
                        'x-requested-with'
                    ) == 'XMLHttpRequest':

                        return JsonResponse(
                            {'error': message},
                            status=400
                        )

                    messages.error(
                        request,
                        message
                    )

                # ------------------------------------------------
                # Création de la note
                # ------------------------------------------------

                else:

                    Note.objects.create(
                        eleve=inscription.eleve,
                        inscription=inscription,
                        annee_scolaire=annee,
                        matiere=matiere,
                        trimestre=trimestre,
                        note_cours=note_cours,
                        note_comp=note_comp
                    )

                    if request.headers.get(
                        'x-requested-with'
                    ) == 'XMLHttpRequest':

                        return JsonResponse({
                            'success':
                                'Note ajoutée avec succès.'
                        })

                    messages.success(
                        request,
                        "Note ajoutée avec succès."
                    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {
        'niveaux': niveaux,
        'groupes': groupes,
        'annees_scolaires': annees_scolaires,
        'matieres': matieres,
        'eleves': eleves,
        'niveau_id': niveau_id,
        'groupe_id': groupe_id,
        'annee_id': annee_id,
    }

    return render(
        request,
        'note/rechercher_eleve.html',
        context
    )


# ============================================================
# LISTE DES NOTES DES ENSEIGNANTS
# ============================================================

def Liste_note_enseignant(request):

    matieres = Matiere.objects.all()

    notes = Note.objects.select_related(
        'eleve',
        'inscription',
        'matiere',
        'annee_scolaire'
    ).all()

    annees = AnneeScolaire.objects.all()

    eleves = EleveInscrit.objects.select_related(
        'eleve',
        'niveau',
        'groupe_classe',
        'annee_scolaire'
    ).all()

    context = {
        'matieres': matieres,
        'notes': notes,
        'annes': annees,
        'eleves': eleves,
    }

    return render(
        request,
        'note/note_enseignant.html',
        context
    )


# ============================================================
# MODIFICATION D'UNE NOTE PAR L'ENSEIGNANT
# ============================================================

@login_required
def modifier_enseignant(request):

    if request.method != 'POST':
        return redirect('note_enseignant')

    note_id = request.POST.get('id')
    inscription_id = request.POST.get('eleve')
    matiere_id = request.POST.get('mat')

    annee_id = (
        request.POST.get('anne')
        or request.POST.get('annee_scolaire')
    )

    note_cours_value = request.POST.get('nc')
    note_comp_value = request.POST.get('nco')
    trimestre = request.POST.get('trimestre')

    # --------------------------------------------------------
    # Vérification
    # --------------------------------------------------------

    if not all([
        note_id,
        inscription_id,
        matiere_id,
        annee_id,
        note_cours_value,
        note_comp_value,
        trimestre
    ]):

        messages.error(
            request,
            "Tous les champs sont obligatoires."
        )

        return redirect('note_enseignant')

    note_obj = get_object_or_404(
        Note,
        id=note_id
    )

    inscription = get_object_or_404(
        EleveInscrit,
        id=inscription_id
    )

    matiere = get_object_or_404(
        Matiere,
        id=matiere_id
    )

    annee = get_object_or_404(
        AnneeScolaire,
        id=annee_id
    )

    # --------------------------------------------------------
    # Conversion
    # --------------------------------------------------------

    try:

        note_cours = float(
            note_cours_value
        )

        note_comp = float(
            note_comp_value
        )

    except (ValueError, TypeError):

        messages.error(
            request,
            "Les notes doivent être numériques."
        )

        return redirect('note_enseignant')

    # --------------------------------------------------------
    # Vérification année
    # --------------------------------------------------------

    if inscription.annee_scolaire_id != annee.id:

        messages.error(
            request,
            "L'élève n'est pas inscrit dans cette année scolaire."
        )

        return redirect('note_enseignant')

    # --------------------------------------------------------
    # Mise à jour
    # --------------------------------------------------------

    note_obj.inscription = inscription
    note_obj.eleve = inscription.eleve
    note_obj.matiere = matiere
    note_obj.annee_scolaire = annee
    note_obj.trimestre = trimestre
    note_obj.note_cours = note_cours
    note_obj.note_comp = note_comp

    note_obj.save()

    messages.success(
        request,
        "La note a été modifiée avec succès."
    )

    return redirect('note_enseignant')


# ============================================================
# SUPPRESSION NOTE ENSEIGNANT
# ============================================================

@login_required
def supprimer_enseignant(request, pk):

    note_obj = get_object_or_404(
        Note,
        id=pk
    )

    note_obj.delete()

    messages.success(
        request,
        "La note a été supprimée avec succès."
    )

    return redirect('note_enseignant')


# ============================================================
# ATTRIBUTION DES NOTES PAR LES ENSEIGNANTS
# ============================================================

@login_required
def attribuer_note_enseignant(request):

    enseignant = getattr(
        request.user,
        'enseignant_profile',
        None
    )

    # --------------------------------------------------------
    # Vérification enseignant
    # --------------------------------------------------------

    if not enseignant:

        messages.error(
            request,
            "Vous n'êtes pas reconnu comme enseignant."
        )

        return render(
            request,
            'note/rechercher_eleve2.html',
            {
                'niveaux': Niveau.objects.none(),
                'groupes': [],
                'annees_scolaires':
                    AnneeScolaire.objects.all(),
                'eleves': None,
                'matieres_autorisees':
                    Matiere.objects.none(),
            }
        )

    # --------------------------------------------------------
    # Niveaux autorisés
    # --------------------------------------------------------

    niveaux_ids = EnseignantMatiere.objects.filter(
        enseignant=enseignant
    ).values_list(
        'niveau_id',
        flat=True
    ).distinct()

    niveaux = Niveau.objects.filter(
        id__in=niveaux_ids
    )

    groupes = []
    eleves = None
    matieres_autorisees = Matiere.objects.none()

    annees_scolaires = AnneeScolaire.objects.all()

    # --------------------------------------------------------
    # Filtres
    # --------------------------------------------------------

    niveau_id = request.GET.get('niveau')
    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')

    # --------------------------------------------------------
    # GROUPES AUTORISÉS
    # --------------------------------------------------------

    if niveau_id:

        try:

            niveau_id = int(niveau_id)

            groupes = GroupeClasse.objects.filter(
                id__in=EnseignantMatiere.objects.filter(
                    enseignant=enseignant,
                    niveau_id=niveau_id
                ).values_list(
                    'groupe_classe_id',
                    flat=True
                )
            ).order_by('nom')

        except (ValueError, TypeError):

            groupes = []

    # --------------------------------------------------------
    # ÉLÈVES ET MATIÈRES
    # --------------------------------------------------------

    if niveau_id and groupe_id and annee_id:

        try:

            groupe_id = int(groupe_id)
            annee_id = int(annee_id)

            eleves = EleveInscrit.objects.filter(
                niveau_id=niveau_id,
                groupe_classe_id=groupe_id,
                annee_scolaire_id=annee_id,
                actif=True
            ).select_related(
                'eleve',
                'niveau',
                'groupe_classe',
                'annee_scolaire'
            )

            matieres_autorisees_ids = (
                EnseignantMatiere.objects.filter(
                    enseignant=enseignant,
                    niveau_id=niveau_id,
                    groupe_classe_id=groupe_id
                ).values_list(
                    'matiere_id',
                    flat=True
                )
            )

            matieres_autorisees = Matiere.objects.filter(
                id__in=matieres_autorisees_ids
            )

        except (ValueError, TypeError):

            eleves = None
            matieres_autorisees = Matiere.objects.none()

    # --------------------------------------------------------
    # ENREGISTREMENT
    # --------------------------------------------------------

    if request.method == 'POST':

        inscription_id = request.POST.get('eleve')

        annee_id_post = (
            request.POST.get('anne')
            or request.POST.get('annee_scolaire')
        )

        matiere_id = request.POST.get('mat')
        trimestre = request.POST.get('trimestre')
        note_cours_value = request.POST.get('nc')
        note_comp_value = request.POST.get('nco')

        # ----------------------------------------------------
        # Vérification champs
        # ----------------------------------------------------

        if not all([
            inscription_id,
            annee_id_post,
            matiere_id,
            trimestre,
            note_cours_value,
            note_comp_value
        ]):

            return JsonResponse(
                {
                    'error':
                        "Veuillez remplir tous les champs."
                },
                status=400
            )

        # ----------------------------------------------------
        # Récupération
        # ----------------------------------------------------

        try:

            inscription = EleveInscrit.objects.select_related(
                'eleve',
                'niveau',
                'groupe_classe',
                'annee_scolaire'
            ).get(
                id=inscription_id
            )

            annee = AnneeScolaire.objects.get(
                id=annee_id_post
            )

            matiere = Matiere.objects.get(
                id=matiere_id
            )

            trimestre = int(trimestre)

            note_cours = float(
                note_cours_value
            )

            note_comp = float(
                note_comp_value
            )

        except (
            EleveInscrit.DoesNotExist,
            AnneeScolaire.DoesNotExist,
            Matiere.DoesNotExist,
            ValueError,
            TypeError
        ):

            return JsonResponse(
                {
                    'error':
                        "Données invalides."
                },
                status=400
            )

        # ----------------------------------------------------
        # Vérification année
        # ----------------------------------------------------

        if inscription.annee_scolaire_id != annee.id:

            return JsonResponse(
                {
                    'error':
                        "Cette inscription ne correspond pas "
                        "à l'année scolaire sélectionnée."
                },
                status=400
            )

        # ----------------------------------------------------
        # Vérification autorisation
        # ----------------------------------------------------

        autorisation = EnseignantMatiere.objects.filter(
            enseignant=enseignant,
            niveau_id=inscription.niveau_id,
            groupe_classe_id=inscription.groupe_classe_id,
            matiere_id=matiere.id
        ).exists()

        if not autorisation:

            return JsonResponse(
                {
                    'error':
                        "Vous n'êtes pas autorisé à noter "
                        "cette matière."
                },
                status=400
            )

        # ----------------------------------------------------
        # Vérification note existante
        # ----------------------------------------------------

        note_existe = Note.objects.filter(
            inscription=inscription,
            matiere=matiere,
            annee_scolaire=annee,
            trimestre=trimestre
        ).exists()

        if note_existe:

            return JsonResponse(
                {
                    'error':
                        "Cet élève est déjà noté pour "
                        "cette matière et ce trimestre."
                },
                status=400
            )

        # ----------------------------------------------------
        # Création
        # ----------------------------------------------------

        Note.objects.create(
            eleve=inscription.eleve,
            inscription=inscription,
            annee_scolaire=annee,
            matiere=matiere,
            trimestre=trimestre,
            note_cours=note_cours,
            note_comp=note_comp
        )

        return JsonResponse(
            {
                'success':
                    "Note ajoutée avec succès."
            }
        )

    # --------------------------------------------------------
    # AFFICHAGE
    # --------------------------------------------------------

    return render(
        request,
        'note/rechercher_eleve2.html',
        {
            'niveaux': niveaux,
            'groupes': groupes,
            'annees_scolaires':
                annees_scolaires,
            'eleves': eleves,
            'matieres_autorisees':
                matieres_autorisees,
            'niveau_id': niveau_id,
            'groupe_id': groupe_id,
            'annee_id': annee_id,
        }
    )


# ============================================================
# AJAX : GROUPES AUTORISÉS
# ============================================================

@login_required
def ajax_groupes(request):

    niveau_id = request.GET.get('niveau')

    enseignant = getattr(
        request.user,
        'enseignant_profile',
        None
    )

    groupes = []

    if niveau_id and enseignant:

        groupes_qs = GroupeClasse.objects.filter(
            id__in=EnseignantMatiere.objects.filter(
                enseignant=enseignant,
                niveau_id=niveau_id
            ).values_list(
                'groupe_classe_id',
                flat=True
            )
        ).order_by('nom')

        groupes = [
            {
                'id': groupe.id,
                'nom': groupe.nom
            }
            for groupe in groupes_qs
        ]

    return JsonResponse(
        groupes,
        safe=False
    )


# ============================================================
# AJAX : MATIÈRES AUTORISÉES
# ============================================================

@login_required
def ajax_matieres(request):

    niveau_id = request.GET.get('niveau')
    groupe_id = request.GET.get('groupe')

    enseignant = getattr(
        request.user,
        'enseignant_profile',
        None
    )

    matieres = []

    if niveau_id and groupe_id and enseignant:

        matieres_qs = EnseignantMatiere.objects.filter(
            enseignant=enseignant,
            niveau_id=niveau_id,
            groupe_classe_id=groupe_id
        ).select_related(
            'matiere'
        )

        matieres = [
            {
                'id': item.matiere.id,
                'nom': item.matiere.nom,
                'coefficient': item.matiere.coefficient,
            }
            for item in matieres_qs
        ]

    return JsonResponse(
        matieres,
        safe=False
    )
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, F

from eleve.models import Eleve,EleveInscrit


from niveau.models import Niveau
from groupe_classe.models import GroupeClasse
from annee_scolaire.models import AnneeScolaire
from note.models import Note

from cycle.models import Cycle, Etablissement

from .models import BulletinTrimestriel, BulletinAnnuel


# ============================================================
# BULLETINS TRIMESTRIELS PAR NIVEAU ET CYCLE
# ============================================================

def bulletins_trimestriels_niveau(request):

    ecoles = Etablissement.objects.all()
    cycles = Cycle.objects.all()
    niveaux = Niveau.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    cycle_id = request.GET.get("cycle")
    niveau_id = request.GET.get("niveau")
    annee_id = request.GET.get("annee_scolaire")
    trimestre = request.GET.get("trimestre")

    bulletins_list = []

    if niveau_id and annee_id and trimestre:

        inscriptions = EleveInscrit.objects.filter(
            annee_scolaire_id=annee_id,
            groupe_classe__niveau_id=niveau_id
        ).select_related(
            "eleve",
            "groupe_classe",
            "groupe_classe__niveau",
            "groupe_classe__niveau__cycle"
        )

        if cycle_id:
            inscriptions = inscriptions.filter(
                groupe_classe__niveau__cycle_id=cycle_id
            )

        for inscription in inscriptions:

            eleve = inscription.eleve

            bulletin, created = BulletinTrimestriel.objects.get_or_create(
                eleve=eleve,
                trimestre=trimestre,
                annee_scolaire_id=annee_id
            )

            bulletins_list.append({
                "bulletin": bulletin,
                "eleve": eleve,
                "inscription": inscription,
                "notes": bulletin.notes_par_matiere,
                "moyenne_totale": bulletin.moyenne_totale or 0,
                "observation": bulletin.observation,
            })

        # Classement
        bulletins_list.sort(
            key=lambda x: x["moyenne_totale"],
            reverse=True
        )

        rang = 0
        previous_moyenne = None

        for index, bulletin in enumerate(
            bulletins_list,
            start=1
        ):

            moyenne = bulletin["moyenne_totale"]

            if moyenne == previous_moyenne:

                bulletin["rang_formate"] = f"{rang}e Ex"

            else:

                rang = index

                suffixe = "er" if rang == 1 else "ème"

                bulletin["rang_formate"] = (
                    f"{rang}{suffixe}"
                )

            previous_moyenne = moyenne

    context = {
        "ecoles": ecoles,
        "cycles": cycles,
        "niveaux": niveaux,
        "annees_scolaires": annees_scolaires,

        "bulletins_trimestriels": bulletins_list,

        "cycle_id": cycle_id,
        "niveau_id": niveau_id,
        "annee_id": annee_id,
        "trimestre": trimestre,

        "cycle_obj": Cycle.objects.filter(
            id=cycle_id
        ).first(),

        "niveau_obj": Niveau.objects.filter(
            id=niveau_id
        ).first(),

        "annee_scolaire_obj": AnneeScolaire.objects.filter(
            id=annee_id
        ).first(),
    }

    return render(
        request,
        "bulletins/bulletins_trimestriels_niveau.html",
        context
    )


# ============================================================
# BULLETINS TRIMESTRIELS PAR CLASSE
# ============================================================

def bulletins_trimestriels_classe(request):

    ecoles = Etablissement.objects.all()

    groupes_classes = GroupeClasse.objects.all()

    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get("groupe_classe")

    annee_id = request.GET.get("annee_scolaire")

    trimestre = request.GET.get("trimestre")

    bulletins_list = []

    if groupe_id and annee_id and trimestre:

        inscriptions = EleveInscrit.objects.filter(
            groupe_classe_id=groupe_id,
            annee_scolaire_id=annee_id
        ).select_related(
            "eleve",
            "groupe_classe"
        )

        for inscription in inscriptions:

            eleve = inscription.eleve

            bulletin, created = BulletinTrimestriel.objects.get_or_create(
                eleve=eleve,
                trimestre=trimestre,
                annee_scolaire_id=annee_id
            )

            bulletins_list.append({
                "bulletin": bulletin,
                "eleve": eleve,
                "inscription": inscription,
                "notes": bulletin.notes_par_matiere,
                "moyenne_totale": bulletin.moyenne_totale or 0,
                "observation": bulletin.observation,
            })

        # Classement
        bulletins_list.sort(
            key=lambda x: x["moyenne_totale"],
            reverse=True
        )

        rang = 0
        previous_moyenne = None

        for index, bulletin in enumerate(
            bulletins_list,
            start=1
        ):

            moyenne = bulletin["moyenne_totale"]

            if moyenne == previous_moyenne:

                bulletin["rang_formate"] = (
                    f"{rang}e Ex"
                )

            else:

                rang = index

                suffixe = (
                    "er"
                    if rang == 1
                    else "ème"
                )

                bulletin["rang_formate"] = (
                    f"{rang}{suffixe}"
                )

            previous_moyenne = moyenne

    context = {
        "ecoles": ecoles,
        "groupes_classes": groupes_classes,
        "annees_scolaires": annees_scolaires,

        "bulletins_trimestriels": bulletins_list,

        "groupe_id": groupe_id,
        "annee_id": annee_id,
        "trimestre": trimestre,
    }

    return render(
        request,
        "bulletins/bulletins_trimestriels_classe.html",
        context
    )


# ============================================================
# RESULTATS TRIMESTRIELS PAR CLASSE
# ============================================================

def resultat_trimestriel_classe(request):

    ecoles = Etablissement.objects.all()

    groupes_classes = GroupeClasse.objects.all()

    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get("groupe_classe")

    annee_id = request.GET.get("annee_scolaire")

    trimestre = request.GET.get("trimestre")

    bulletins_list = []

    groupe_obj = None

    annee_scolaire_obj = None

    trimestre_label = ""

    statistiques = {
        "total_inscrits": 0,
        "ayant_composes": 0,
        "admis": 0,
        "non_admis": 0,
        "taux_reussite": 0,
        "taux_echec": 0,

        "filles_total": 0,
        "filles_composes": 0,
        "filles_admis": 0,
        "filles_non_admis": 0,
        "taux_filles_reussite": 0,
        "taux_filles_echec": 0,
    }

    if groupe_id and annee_id and trimestre:

        groupe_obj = GroupeClasse.objects.filter(
            id=groupe_id
        ).first()

        annee_scolaire_obj = AnneeScolaire.objects.filter(
            id=annee_id
        ).first()

        trimestre_label = f"Trimestre {trimestre}"

        # --------------------------------------------
        # INSCRIPTIONS
        # --------------------------------------------

        inscriptions = EleveInscrit.objects.filter(
            groupe_classe_id=groupe_id,
            annee_scolaire_id=annee_id
        ).select_related(
            "eleve",
            "groupe_classe__niveau__cycle"
        )

        eleves = [
            inscription.eleve
            for inscription in inscriptions
        ]

        # --------------------------------------------
        # SEUIL D'ADMISSION
        # --------------------------------------------

        seuil_admission = 10

        if (
            groupe_obj
            and groupe_obj.niveau
            and groupe_obj.niveau.cycle
            and groupe_obj.niveau.cycle.nom.lower()
            == "primaire"
        ):
            seuil_admission = 5

        # --------------------------------------------
        # BULLETINS
        # --------------------------------------------

        bulletins = BulletinTrimestriel.objects.filter(
            eleve__in=eleves,
            annee_scolaire_id=annee_id,
            trimestre=trimestre
        ).select_related(
            "eleve"
        )

        for bulletin in bulletins:

            moyenne = bulletin.moyenne_totale or 0

            bulletins_list.append({
                "bulletin": bulletin,
                "eleve": bulletin.eleve,
                "moyenne": moyenne,
                "observation": (
                    bulletin.observation
                    or "Non disponible"
                ),
            })

        # --------------------------------------------
        # CLASSEMENT
        # --------------------------------------------

        bulletins_list.sort(
            key=lambda x: x["moyenne"],
            reverse=True
        )

        rang = 0

        previous_moyenne = None

        for index, bulletin in enumerate(
            bulletins_list,
            start=1
        ):

            moyenne = bulletin["moyenne"]

            if moyenne == previous_moyenne:

                bulletin["rang"] = (
                    f"{rang}e Ex"
                )

            else:

                rang = index

                suffixe = (
                    "er"
                    if rang == 1
                    else "ème"
                )

                bulletin["rang"] = (
                    f"{rang}{suffixe}"
                )

            previous_moyenne = moyenne

        # --------------------------------------------
        # STATISTIQUES GENERALES
        # --------------------------------------------

        statistiques["total_inscrits"] = len(eleves)

        composes = [
            bulletin
            for bulletin in bulletins_list
            if bulletin["moyenne"] > 0
        ]

        statistiques["ayant_composes"] = len(
            composes
        )

        statistiques["admis"] = len([
            bulletin
            for bulletin in composes
            if bulletin["moyenne"]
            >= seuil_admission
        ])

        statistiques["non_admis"] = (
            statistiques["ayant_composes"]
            - statistiques["admis"]
        )

        if statistiques["ayant_composes"] > 0:

            statistiques["taux_reussite"] = round(
                statistiques["admis"]
                / statistiques["ayant_composes"]
                * 100,
                2
            )

            statistiques["taux_echec"] = round(
                statistiques["non_admis"]
                / statistiques["ayant_composes"]
                * 100,
                2
            )

        # --------------------------------------------
        # STATISTIQUES FILLES
        # --------------------------------------------

        filles = [
            eleve
            for eleve in eleves
            if (eleve.genre or "").lower()
            == "femme"
        ]

        statistiques["filles_total"] = len(
            filles
        )

        filles_composes = [
            bulletin
            for bulletin in composes
            if (
                bulletin["eleve"].genre
                or ""
            ).lower() == "femme"
        ]

        statistiques["filles_composes"] = len(
            filles_composes
        )

        filles_admis = [
            bulletin
            for bulletin in filles_composes
            if bulletin["moyenne"]
            >= seuil_admission
        ]

        statistiques["filles_admis"] = len(
            filles_admis
        )

        statistiques["filles_non_admis"] = (
            statistiques["filles_composes"]
            - statistiques["filles_admis"]
        )

        if statistiques["filles_composes"] > 0:

            statistiques["taux_filles_reussite"] = round(
                statistiques["filles_admis"]
                / statistiques["filles_composes"]
                * 100,
                2
            )

            statistiques["taux_filles_echec"] = round(
                statistiques["filles_non_admis"]
                / statistiques["filles_composes"]
                * 100,
                2
            )

    context = {
        "groupes_classes": groupes_classes,
        "annees_scolaires": annees_scolaires,

        "sorted_bulletins": bulletins_list,

        "groupe_id": groupe_id,
        "annee_id": annee_id,
        "trimestre": trimestre,

        "groupe_obj": groupe_obj,
        "annee_scolaire_obj": annee_scolaire_obj,

        "trimestre_label": trimestre_label,

        "statistiques": statistiques,

        "ecoles": ecoles,
    }

    return render(
        request,
        "bulletins/resultat_trimestriel_classe.html",
        context
    )


# ============================================================
# RESULTATS ANNUELS PAR CLASSE
# ============================================================

def resultat_annuel_classe(request):

    ecoles = Etablissement.objects.all()

    groupes_classes = GroupeClasse.objects.all()

    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get("groupe_classe")

    annee_id = request.GET.get("annee_scolaire")

    bulletins_list = []

    groupe_obj = None

    annee_scolaire_obj = None

    statistiques = {
        "total_inscrits": 0,
        "ayant_composes": 0,
        "admis": 0,
        "non_admis": 0,
        "taux_reussite": 0,
        "taux_echec": 0,

        "filles_total": 0,
        "filles_composes": 0,
        "filles_admis": 0,
        "filles_non_admis": 0,
        "taux_filles_reussite": 0,
        "taux_filles_echec": 0,
    }

    if groupe_id and annee_id:

        groupe_obj = GroupeClasse.objects.filter(
            id=groupe_id
        ).first()

        annee_scolaire_obj = AnneeScolaire.objects.filter(
            id=annee_id
        ).first()

        # --------------------------------------------
        # INSCRIPTIONS
        # --------------------------------------------

        inscriptions = EleveInscrit.objects.filter(
            groupe_classe_id=groupe_id,
            annee_scolaire_id=annee_id
        ).select_related(
            "eleve",
            "groupe_classe__niveau__cycle"
        )

        eleves = [
            inscription.eleve
            for inscription in inscriptions
        ]

        # --------------------------------------------
        # SEUIL
        # --------------------------------------------

        seuil_admission = 10

        if (
            groupe_obj
            and groupe_obj.niveau
            and groupe_obj.niveau.cycle
            and groupe_obj.niveau.cycle.nom.lower()
            == "primaire"
        ):
            seuil_admission = 5

        # --------------------------------------------
        # BULLETINS
        # --------------------------------------------

        bulletins = BulletinAnnuel.objects.filter(
            eleve__in=eleves,
            annee_scolaire_id=annee_id
        ).select_related(
            "eleve"
        )

        for bulletin in bulletins:

            moyenne = (
                bulletin.moyenne_totale_annuelle
                or 0
            )

            bulletins_list.append({
                "bulletin": bulletin,
                "eleve": bulletin.eleve,
                "moyenne": moyenne,
                "observation": (
                    bulletin.observation_finale
                    or "Non disponible"
                ),
            })

        # --------------------------------------------
        # CLASSEMENT
        # --------------------------------------------

        bulletins_list.sort(
            key=lambda x: x["moyenne"],
            reverse=True
        )

        rang = 0

        previous_moyenne = None

        for index, bulletin in enumerate(
            bulletins_list,
            start=1
        ):

            moyenne = bulletin["moyenne"]

            if moyenne == previous_moyenne:

                bulletin["rang"] = (
                    f"{rang}e Ex"
                )

            else:

                rang = index

                suffixe = (
                    "er"
                    if rang == 1
                    else "ème"
                )

                bulletin["rang"] = (
                    f"{rang}{suffixe}"
                )

            previous_moyenne = moyenne

        # --------------------------------------------
        # STATISTIQUES
        # --------------------------------------------

        statistiques["total_inscrits"] = len(
            eleves
        )

        composes = [
            bulletin
            for bulletin in bulletins_list
            if bulletin["moyenne"] > 0
        ]

        statistiques["ayant_composes"] = len(
            composes
        )

        statistiques["admis"] = len([
            bulletin
            for bulletin in composes
            if bulletin["moyenne"]
            >= seuil_admission
        ])

        statistiques["non_admis"] = (
            statistiques["ayant_composes"]
            - statistiques["admis"]
        )

        if statistiques["ayant_composes"] > 0:

            statistiques["taux_reussite"] = round(
                statistiques["admis"]
                / statistiques["ayant_composes"]
                * 100,
                2
            )

            statistiques["taux_echec"] = round(
                statistiques["non_admis"]
                / statistiques["ayant_composes"]
                * 100,
                2
            )

        # --------------------------------------------
        # FILLES
        # --------------------------------------------

        filles = [
            eleve
            for eleve in eleves
            if (eleve.genre or "").lower()
            == "femme"
        ]

        statistiques["filles_total"] = len(
            filles
        )

        filles_composes = [
            bulletin
            for bulletin in composes
            if (
                bulletin["eleve"].genre
                or ""
            ).lower() == "femme"
        ]

        statistiques["filles_composes"] = len(
            filles_composes
        )

        filles_admis = [
            bulletin
            for bulletin in filles_composes
            if bulletin["moyenne"]
            >= seuil_admission
        ]

        statistiques["filles_admis"] = len(
            filles_admis
        )

        statistiques["filles_non_admis"] = (
            statistiques["filles_composes"]
            - statistiques["filles_admis"]
        )

        if statistiques["filles_composes"] > 0:

            statistiques["taux_filles_reussite"] = round(
                statistiques["filles_admis"]
                / statistiques["filles_composes"]
                * 100,
                2
            )

            statistiques["taux_filles_echec"] = round(
                statistiques["filles_non_admis"]
                / statistiques["filles_composes"]
                * 100,
                2
            )

    context = {
        "groupes_classes": groupes_classes,
        "annees_scolaires": annees_scolaires,

        "sorted_bulletins": bulletins_list,

        "groupe_id": groupe_id,
        "annee_id": annee_id,

        "groupe_obj": groupe_obj,
        "annee_scolaire_obj": annee_scolaire_obj,

        "statistiques": statistiques,

        "ecoles": ecoles,
    }

    return render(
        request,
        "bulletins/resultat_annuel_classe.html",
        context
    )


# ============================================================
# VALIDATION BULLETIN TRIMESTRIEL
# ============================================================

def valider_bulletin_trimestre(request):

    if request.method == "POST":

        annee_id = request.POST.get(
            "annee_scolaire"
        )

        groupe_id = request.POST.get(
            "groupe_classe"
        )

        trimestre = request.POST.get(
            "trimestre"
        )

        inscriptions = EleveInscrit.objects.filter(
            groupe_classe_id=groupe_id,
            annee_scolaire_id=annee_id
        )

        for inscription in inscriptions:

            BulletinTrimestriel.objects.get_or_create(
                eleve=inscription.eleve,
                trimestre=trimestre,
                annee_scolaire_id=annee_id
            )

        messages.success(
            request,
            "Bulletins trimestriels validés."
        )

        return redirect("trimestre")

    context = {
        "groupes_classes": GroupeClasse.objects.all(),
        "annees_scolaires": AnneeScolaire.objects.all(),
    }

    return render(
        request,
        "bulletins/valider_bulletin_trimestre.html",
        context
    )


# ============================================================
# VALIDATION BULLETIN ANNUEL
# ============================================================

def valider_bulletin_annuel(request):

    if request.method == "POST":

        annee_id = request.POST.get(
            "annee_scolaire"
        )

        groupe_id = request.POST.get(
            "groupe_classe"
        )

        inscriptions = EleveInscrit.objects.filter(
            groupe_classe_id=groupe_id,
            annee_scolaire_id=annee_id
        )

        for inscription in inscriptions:

            BulletinAnnuel.objects.get_or_create(
                eleve=inscription.eleve,
                annee_scolaire_id=annee_id
            )

        messages.success(
            request,
            "Bulletins annuels validés."
        )

        return redirect(
            "valider_bulletin"
        )

    context = {
        "groupes_classes": GroupeClasse.objects.all(),
        "annees_scolaires": AnneeScolaire.objects.all(),
    }

    return render(
        request,
        "bulletins/valider_bulletin_annuel.html",
        context
    )


# ============================================================
# RESULTATS TRIMESTRIELS PAR NIVEAU
# ============================================================

def resultats_trimestriels_niveau(request):

    ecoles = Etablissement.objects.all()

    niveaux = Niveau.objects.all()

    annees_scolaires = AnneeScolaire.objects.all()

    niveau_id = request.GET.get("niveau")

    annee_id = request.GET.get(
        "annee_scolaire"
    )

    trimestre = request.GET.get(
        "trimestre"
    )

    bulletins_list = []

    niveau_obj = None

    annee_scolaire_obj = None

    trimestre_label = ""

    statistiques = {
        "total_inscrits": 0,
        "ayant_composes": 0,
        "admis": 0,
        "non_admis": 0,
        "taux_reussite": 0,
        "taux_echec": 0,

        "filles_total": 0,
        "filles_composes": 0,
        "filles_admis": 0,
        "filles_non_admis": 0,
        "taux_filles_reussite": 0,
        "taux_filles_echec": 0,
    }

    stats_par_cycle = []

    if niveau_id and annee_id and trimestre:

        niveau_obj = Niveau.objects.filter(
            id=niveau_id
        ).first()

        annee_scolaire_obj = AnneeScolaire.objects.filter(
            id=annee_id
        ).first()

        trimestre_label = (
            f"Trimestre {trimestre}"
        )

        # --------------------------------------------
        # SEUIL
        # --------------------------------------------

        seuil_admission = 10

        if (
            niveau_obj
            and niveau_obj.cycle
            and niveau_obj.cycle.nom.lower()
            == "primaire"
        ):
            seuil_admission = 5

        # --------------------------------------------
        # INSCRIPTIONS DU NIVEAU
        # --------------------------------------------

        inscriptions = EleveInscrit.objects.filter(
            annee_scolaire_id=annee_id,
            groupe_classe__niveau_id=niveau_id
        ).select_related(
            "eleve",
            "groupe_classe__niveau__cycle"
        )

        eleves = [
            inscription.eleve
            for inscription in inscriptions
        ]

        # --------------------------------------------
        # BULLETINS
        # --------------------------------------------

        bulletins = BulletinTrimestriel.objects.filter(
            eleve__in=eleves,
            trimestre=trimestre,
            annee_scolaire_id=annee_id
        ).select_related(
            "eleve"
        )

        for bulletin in bulletins:

            bulletins_list.append({
                "bulletin": bulletin,
                "eleve": bulletin.eleve,
                "moyenne": (
                    bulletin.moyenne_totale
                    or 0
                ),
                "observation": (
                    bulletin.observation
                    or "Non disponible"
                ),
            })

        # --------------------------------------------
        # CLASSEMENT
        # --------------------------------------------

        bulletins_list.sort(
            key=lambda x: x["moyenne"],
            reverse=True
        )

        rang = 0

        previous_moyenne = None

        for index, bulletin in enumerate(
            bulletins_list,
            start=1
        ):

            moyenne = bulletin["moyenne"]

            if moyenne == previous_moyenne:

                bulletin["rang"] = (
                    f"{rang}e Ex"
                )

            else:

                rang = index

                suffixe = (
                    "er"
                    if rang == 1
                    else "ème"
                )

                bulletin["rang"] = (
                    f"{rang}{suffixe}"
                )

            previous_moyenne = moyenne

        # --------------------------------------------
        # STATISTIQUES
        # --------------------------------------------

        statistiques["total_inscrits"] = len(
            eleves
        )

        composes = [
            bulletin
            for bulletin in bulletins_list
            if bulletin["moyenne"] > 0
        ]

        statistiques["ayant_composes"] = len(
            composes
        )

        statistiques["admis"] = len([
            bulletin
            for bulletin in composes
            if bulletin["moyenne"]
            >= seuil_admission
        ])

        statistiques["non_admis"] = (
            statistiques["ayant_composes"]
            - statistiques["admis"]
        )

        if statistiques["ayant_composes"] > 0:

            statistiques["taux_reussite"] = round(
                statistiques["admis"]
                / statistiques["ayant_composes"]
                * 100,
                2
            )

            statistiques["taux_echec"] = round(
                statistiques["non_admis"]
                / statistiques["ayant_composes"]
                * 100,
                2
            )

        # --------------------------------------------
        # FILLES
        # --------------------------------------------

        filles = [
            eleve
            for eleve in eleves
            if (eleve.genre or "").lower()
            == "femme"
        ]

        statistiques["filles_total"] = len(
            filles
        )

        filles_composes = [
            bulletin
            for bulletin in composes
            if (
                bulletin["eleve"].genre
                or ""
            ).lower() == "femme"
        ]

        statistiques["filles_composes"] = len(
            filles_composes
        )

        filles_admis = [
            bulletin
            for bulletin in filles_composes
            if bulletin["moyenne"]
            >= seuil_admission
        ]

        statistiques["filles_admis"] = len(
            filles_admis
        )

        statistiques["filles_non_admis"] = (
            statistiques["filles_composes"]
            - statistiques["filles_admis"]
        )

        if statistiques["filles_composes"] > 0:

            statistiques["taux_filles_reussite"] = round(
                statistiques["filles_admis"]
                / statistiques["filles_composes"]
                * 100,
                2
            )

            statistiques["taux_filles_echec"] = round(
                statistiques["filles_non_admis"]
                / statistiques["filles_composes"]
                * 100,
                2
            )

        # --------------------------------------------
        # STATISTIQUES PAR CYCLE
        # --------------------------------------------

        cycles = Cycle.objects.all()

        for cycle in cycles:

            inscriptions_cycle = EleveInscrit.objects.filter(
                annee_scolaire_id=annee_id,
                groupe_classe__niveau_id=niveau_id,
                groupe_classe__niveau__cycle=cycle
            ).select_related("eleve")

            eleves_cycle = [
                inscription.eleve
                for inscription in inscriptions_cycle
            ]

            bulletins_cycle = BulletinTrimestriel.objects.filter(
                eleve__in=eleves_cycle,
                trimestre=trimestre,
                annee_scolaire_id=annee_id
            )

            seuil_cycle = (
                5
                if cycle.nom.lower() == "primaire"
                else 10
            )

            composes_cycle = [
                bulletin
                for bulletin in bulletins_cycle
                if (
                    bulletin.moyenne_totale
                    and bulletin.moyenne_totale > 0
                )
            ]

            admis_cycle = [
                bulletin
                for bulletin in composes_cycle
                if bulletin.moyenne_totale
                >= seuil_cycle
            ]

            stats_par_cycle.append({
                "cycle": cycle.nom,
                "total": len(eleves_cycle),
                "ayant_composes": len(
                    composes_cycle
                ),
                "admis": len(
                    admis_cycle
                ),
                "taux_reussite": (
                    round(
                        len(admis_cycle)
                        / len(composes_cycle)
                        * 100,
                        2
                    )
                    if composes_cycle
                    else 0
                ),
            })

    context = {
        "niveaux": niveaux,
        "annees_scolaires": annees_scolaires,

        "sorted_bulletins": bulletins_list,

        "niveau_id": niveau_id,
        "annee_id": annee_id,
        "trimestre": trimestre,

        "niveau_obj": niveau_obj,
        "annee_scolaire_obj": annee_scolaire_obj,

        "trimestre_label": trimestre_label,

        "statistiques": statistiques,

        "stats_par_cycle": stats_par_cycle,

        "ecoles": ecoles,
    }

    return render(
        request,
        "bulletins/resultats_trimestriels_niveau.html",
        context
    )


# ============================================================
# RESULTATS ANNUELS PAR NIVEAU
# ============================================================

def resultats_annuels_niveau(request):

    ecoles = Etablissement.objects.all()

    niveaux = Niveau.objects.all()

    annees_scolaires = AnneeScolaire.objects.all()

    niveau_id = request.GET.get("niveau")

    annee_id = request.GET.get(
        "annee_scolaire"
    )

    bulletins_list = []

    niveau_obj = None

    annee_scolaire_obj = None

    statistiques = {
        "total_inscrits": 0,
        "ayant_composes": 0,
        "admis": 0,
        "non_admis": 0,
        "taux_reussite": 0,
        "taux_echec": 0,

        "filles_total": 0,
        "filles_composes": 0,
        "filles_admis": 0,
        "filles_non_admis": 0,
        "taux_filles_reussite": 0,
        "taux_filles_echec": 0,
    }

    if niveau_id and annee_id:

        niveau_obj = Niveau.objects.filter(
            id=niveau_id
        ).first()

        annee_scolaire_obj = AnneeScolaire.objects.filter(
            id=annee_id
        ).first()

        # --------------------------------------------
        # INSCRIPTIONS
        # --------------------------------------------

        inscriptions = EleveInscrit.objects.filter(
            annee_scolaire_id=annee_id,
            groupe_classe__niveau_id=niveau_id
        ).select_related(
            "eleve",
            "groupe_classe"
        )

        eleves = [
            inscription.eleve
            for inscription in inscriptions
        ]

        # --------------------------------------------
        # SEUIL
        # --------------------------------------------

        seuil_admission = 10

        if (
            niveau_obj
            and niveau_obj.cycle
            and niveau_obj.cycle.nom.lower()
            == "primaire"
        ):
            seuil_admission = 5

        # --------------------------------------------
        # BULLETINS
        # --------------------------------------------

        bulletins = BulletinAnnuel.objects.filter(
            eleve__in=eleves,
            annee_scolaire_id=annee_id
        ).select_related(
            "eleve"
        )

        for bulletin in bulletins:

            moyenne = (
                bulletin.moyenne_totale_annuelle
                or 0
            )

            bulletins_list.append({
                "bulletin": bulletin,
                "eleve": bulletin.eleve,
                "moyenne_totale": moyenne,
                "observation": (
                    bulletin.observation_finale
                    or "Non disponible"
                ),
            })

        # --------------------------------------------
        # CLASSEMENT
        # --------------------------------------------

        bulletins_list.sort(
            key=lambda x: x["moyenne_totale"],
            reverse=True
        )

        rang = 0

        previous_moyenne = None

        for index, bulletin in enumerate(
            bulletins_list,
            start=1
        ):

            moyenne = bulletin[
                "moyenne_totale"
            ]

            if moyenne == previous_moyenne:

                bulletin["rang"] = (
                    f"{rang}e Ex"
                )

            else:

                rang = index

                suffixe = (
                    "er"
                    if rang == 1
                    else "ème"
                )

                bulletin["rang"] = (
                    f"{rang}{suffixe}"
                )

            previous_moyenne = moyenne

        # --------------------------------------------
        # STATISTIQUES
        # --------------------------------------------

        statistiques["total_inscrits"] = len(
            eleves
        )

        composes = [
            bulletin
            for bulletin in bulletins_list
            if bulletin["moyenne_totale"] > 0
        ]

        statistiques["ayant_composes"] = len(
            composes
        )

        statistiques["admis"] = len([
            bulletin
            for bulletin in composes
            if bulletin["moyenne_totale"]
            >= seuil_admission
        ])

        statistiques["non_admis"] = (
            statistiques["ayant_composes"]
            - statistiques["admis"]
        )

        if statistiques["ayant_composes"] > 0:

            statistiques["taux_reussite"] = round(
                statistiques["admis"]
                / statistiques["ayant_composes"]
                * 100,
                2
            )

            statistiques["taux_echec"] = round(
                statistiques["non_admis"]
                / statistiques["ayant_composes"]
                * 100,
                2
            )

        # --------------------------------------------
        # FILLES
        # --------------------------------------------

        filles = [
            eleve
            for eleve in eleves
            if (eleve.genre or "").lower()
            == "femme"
        ]

        statistiques["filles_total"] = len(
            filles
        )

        filles_composes = [
            bulletin
            for bulletin in composes
            if (
                bulletin["eleve"].genre
                or ""
            ).lower() == "femme"
        ]

        statistiques["filles_composes"] = len(
            filles_composes
        )

        filles_admis = [
            bulletin
            for bulletin in filles_composes
            if bulletin["moyenne_totale"]
            >= seuil_admission
        ]

        statistiques["filles_admis"] = len(
            filles_admis
        )

        statistiques["filles_non_admis"] = (
            statistiques["filles_composes"]
            - statistiques["filles_admis"]
        )

        if statistiques["filles_composes"] > 0:

            statistiques["taux_filles_reussite"] = round(
                statistiques["filles_admis"]
                / statistiques["filles_composes"]
                * 100,
                2
            )

            statistiques["taux_filles_echec"] = round(
                statistiques["filles_non_admis"]
                / statistiques["filles_composes"]
                * 100,
                2
            )

    context = {
        "niveaux": niveaux,
        "annees_scolaires": annees_scolaires,

        "bulletins": bulletins_list,

        "niveau_selectionne": (
            int(niveau_id)
            if niveau_id
            else None
        ),

        "annee_scolaire_selectionnee": (
            int(annee_id)
            if annee_id
            else None
        ),

        "niveau_obj": niveau_obj,

        "annee_scolaire_obj": (
            annee_scolaire_obj
        ),

        "statistiques": statistiques,

        "ecoles": ecoles,
    }

    return render(
        request,
        "bulletins/resultats_annuels_niveau.html",
        context
    )



from django.shortcuts import render
from django.db.models import Avg, F, ExpressionWrapper, FloatField

# ============================================================
# BULLETINS ANNUELS PAR NIVEAU
# ============================================================

def bulletins_annuels_niveau(request):

    # ========================================================
    # DONNÉES POUR LES FILTRES
    # ========================================================

    cycles = Cycle.objects.all()

    niveaux = Niveau.objects.all()

    annees_scolaires = AnneeScolaire.objects.all()

    ecoles = Etablissement.objects.all()


    # ========================================================
    # RÉCUPÉRATION DES PARAMÈTRES
    # ========================================================

    cycle_id = request.GET.get("cycle")

    niveau_id = request.GET.get("niveau")

    annee_id = request.GET.get("annee_scolaire")


    # ========================================================
    # LISTE DES BULLETINS
    # ========================================================

    bulletins_list = []


    # ========================================================
    # SI UN NIVEAU ET UNE ANNÉE SONT SÉLECTIONNÉS
    # ========================================================

    if niveau_id and annee_id:

        # ----------------------------------------------------
        # RÉCUPÉRER LES INSCRIPTIONS
        # ----------------------------------------------------

        inscriptions = (
            EleveInscrit.objects
            .filter(
                annee_scolaire_id=annee_id,
                groupe_classe__niveau_id=niveau_id
            )
            .select_related(
                "eleve",
                "groupe_classe",
                "groupe_classe__niveau",
                "groupe_classe__niveau__cycle"
            )
        )


        # ----------------------------------------------------
        # FILTRE PAR CYCLE
        # ----------------------------------------------------

        if cycle_id:

            inscriptions = inscriptions.filter(
                groupe_classe__niveau__cycle_id=cycle_id
            )


        # ====================================================
        # TRAITEMENT DE CHAQUE ÉLÈVE
        # ====================================================

        for inscription in inscriptions:

            eleve = inscription.eleve


            # ------------------------------------------------
            # BULLETIN ANNUEL
            # ------------------------------------------------

            bulletin, created = (
                BulletinAnnuel.objects.get_or_create(
                    eleve=eleve,
                    annee_scolaire_id=annee_id
                )
            )


            # ------------------------------------------------
            # MOYENNES DES 3 TRIMESTRES
            # ------------------------------------------------

            moyennes_trimestrielles = []


            for trimestre in range(1, 4):

                # ============================================
                # NOTES DU TRIMESTRE
                # ============================================

                notes = Note.objects.filter(
                    eleve=eleve,
                    annee_scolaire_id=annee_id,
                    trimestre=trimestre
                )


                # ============================================
                # MOYENNE DE CHAQUE MATIÈRE
                #
                # (note_cours + note_comp) / 2
                # ============================================

                moyennes_matieres = (
                    notes
                    .values("matiere_id")
                    .annotate(
                        moyenne_matiere=ExpressionWrapper(
                            (
                                F("note_cours") +
                                F("note_comp")
                            ) / 2.0,
                            output_field=FloatField()
                        )
                    )
                )


                # ============================================
                # MOYENNE GÉNÉRALE DU TRIMESTRE
                #
                # On fait la moyenne des moyennes
                # de toutes les matières.
                # ============================================

                moyenne = (
                    moyennes_matieres
                    .aggregate(
                        moyenne=Avg("moyenne_matiere")
                    )
                    ["moyenne"]
                )


                # ============================================
                # AJOUT DE LA MOYENNE
                # ============================================

                if moyenne is not None:

                    moyennes_trimestrielles.append(
                        round(float(moyenne), 2)
                    )

                else:

                    moyennes_trimestrielles.append(0)


            # =================================================
            # MOYENNE ANNUELLE
            # =================================================

            moyenne_annuelle = (
                bulletin.moyenne_totale_annuelle
                if bulletin.moyenne_totale_annuelle is not None
                else 0
            )


            # =================================================
            # OBSERVATION
            # =================================================

            observation = (
                bulletin.observation_finale
                if bulletin.observation_finale
                else "Non disponible"
            )


            # =================================================
            # AJOUT À LA LISTE
            # =================================================

            bulletins_list.append({

                "eleve": eleve,

                "inscription": inscription,

                "bulletin": bulletin,

                "moyennes_trimestrielles":
                    moyennes_trimestrielles,

                "moyenne_annuelle":
                    moyenne_annuelle,

                "observation":
                    observation,
            })


        # ====================================================
        # CLASSEMENT DES ÉLÈVES
        # ====================================================

        bulletins_list.sort(
            key=lambda x: x["moyenne_annuelle"],
            reverse=True
        )


        # ====================================================
        # ATTRIBUTION DES RANGS
        # ====================================================

        rang = 0

        previous_moyenne = None


        for index, bulletin in enumerate(
            bulletins_list,
            start=1
        ):

            moyenne = bulletin[
                "moyenne_annuelle"
            ]


            # ------------------------------------------------
            # EX ÆQUO
            # ------------------------------------------------

            if (
                previous_moyenne is not None
                and moyenne == previous_moyenne
            ):

                bulletin["rang"] = (
                    f"{rang}e Ex"
                )


            # ------------------------------------------------
            # NOUVEAU RANG
            # ------------------------------------------------

            else:

                rang = index

                if rang == 1:

                    suffixe = "er"

                else:

                    suffixe = "ème"

                bulletin["rang"] = (
                    f"{rang}{suffixe}"
                )


            previous_moyenne = moyenne


    # ========================================================
    # OBJETS DES FILTRES SÉLECTIONNÉS
    # ========================================================

    cycle_obj = None

    niveau_obj = None

    annee_scolaire_obj = None


    if cycle_id:

        cycle_obj = (
            Cycle.objects
            .filter(id=cycle_id)
            .first()
        )


    if niveau_id:

        niveau_obj = (
            Niveau.objects
            .filter(id=niveau_id)
            .first()
        )


    if annee_id:

        annee_scolaire_obj = (
            AnneeScolaire.objects
            .filter(id=annee_id)
            .first()
        )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "ecoles":
            ecoles,

        "cycles":
            cycles,

        "niveaux":
            niveaux,

        "annees_scolaires":
            annees_scolaires,

        "bulletins_annuels":
            bulletins_list,

        "cycle_id":
            cycle_id,

        "niveau_id":
            niveau_id,

        "annee_scolaire_id":
            annee_id,

        "cycle_obj":
            cycle_obj,

        "niveau_obj":
            niveau_obj,

        "annee_scolaire_obj":
            annee_scolaire_obj,
    }


    # ========================================================
    # AFFICHAGE
    # ========================================================

    return render(
        request,
        "bulletins/bulletins_annuel_niveau.html",
        context
    )




# ============================================================
# BULLETINS ANNUELS PAR CLASSE
# ============================================================



# ============================================================
# BULLETINS ANNUELS PAR CLASSE
# ============================================================

def bulletins_annuels_classe(request):

    ecoles = Etablissement.objects.all()

    groupes = GroupeClasse.objects.all()

    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get("groupe")

    annee_id = request.GET.get("annee_scolaire")

    bulletins_list = []


    # ========================================================
    # FILTRE CLASSE + ANNÉE
    # ========================================================

    if groupe_id and annee_id:

        inscriptions = (
            EleveInscrit.objects
            .filter(
                groupe_classe_id=groupe_id,
                annee_scolaire_id=annee_id
            )
            .select_related(
                "eleve",
                "groupe_classe"
            )
        )


        # ====================================================
        # PARCOURIR LES ÉLÈVES
        # ====================================================

        for inscription in inscriptions:

            eleve = inscription.eleve


            # =================================================
            # BULLETIN ANNUEL
            # =================================================

            bulletin, created = (
                BulletinAnnuel.objects.get_or_create(
                    eleve=eleve,
                    annee_scolaire_id=annee_id
                )
            )


            # =================================================
            # MOYENNES DES 3 TRIMESTRES
            # =================================================

            moyennes_trimestrielles = []


            for trimestre in range(1, 4):

                # ---------------------------------------------
                # NOTES DE L'ÉLÈVE POUR LE TRIMESTRE
                # ---------------------------------------------

                notes = (
                    Note.objects
                    .filter(
                        eleve=eleve,
                        annee_scolaire_id=annee_id,
                        trimestre=trimestre
                    )
                )


                # ---------------------------------------------
                # MOYENNE PAR MATIÈRE
                # ---------------------------------------------

                moyennes_matieres = (
                    notes
                    .values("matiere_id")
                    .annotate(
                        moyenne_matiere=Avg(
                            "note_finale"
                        )
                    )
                )


                # ---------------------------------------------
                # MOYENNE DU TRIMESTRE
                # ---------------------------------------------

                moyenne = (
                    moyennes_matieres
                    .aggregate(
                        moyenne=Avg(
                            "moyenne_matiere"
                        )
                    )
                    ["moyenne"]
                )


                if moyenne is not None:

                    moyenne = round(
                        float(moyenne),
                        2
                    )

                else:

                    moyenne = 0


                moyennes_trimestrielles.append(
                    moyenne
                )


            # =================================================
            # MOYENNE ANNUELLE
            # =================================================

            moyennes_existantes = [
                m
                for m in moyennes_trimestrielles
                if m is not None
            ]


            if moyennes_existantes:

                moyenne_annuelle = round(
                    sum(moyennes_existantes)
                    / len(moyennes_existantes),
                    2
                )

            else:

                moyenne_annuelle = 0


            # =================================================
            # OBSERVATION
            # =================================================

            if moyenne_annuelle >= 16:

                observation = "Très bien"

            elif moyenne_annuelle >= 14:

                observation = "Bien"

            elif moyenne_annuelle >= 12:

                observation = "Assez bien"

            elif moyenne_annuelle >= 10:

                observation = "Passable"

            else:

                observation = "Insuffisant"


            # =================================================
            # AJOUT DU BULLETIN
            # =================================================

            bulletins_list.append({

                "eleve":
                    eleve,

                "inscription":
                    inscription,

                "bulletin":
                    bulletin,

                "moyennes_trimestrielles":
                    moyennes_trimestrielles,

                "moyenne_annuelle":
                    moyenne_annuelle,

                "observation":
                    observation,

                "rang":
                    ""
            })


        # ====================================================
        # CLASSEMENT
        # ====================================================

        bulletins_list.sort(
            key=lambda x:
                x["moyenne_annuelle"],
            reverse=True
        )


        # ====================================================
        # RANG
        # ====================================================

        rang = 0

        previous_moyenne = None


        for index, bulletin in enumerate(
            bulletins_list,
            start=1
        ):

            moyenne = bulletin[
                "moyenne_annuelle"
            ]


            if (
                previous_moyenne is not None
                and moyenne == previous_moyenne
            ):

                bulletin["rang"] = (
                    f"{rang}e Ex"
                )

            else:

                rang = index

                if rang == 1:

                    bulletin["rang"] = "1er"

                else:

                    bulletin["rang"] = (
                        f"{rang}ème"
                    )


            previous_moyenne = moyenne


    # ========================================================
    # GROUPE
    # ========================================================

    groupe_obj = None

    if groupe_id:

        groupe_obj = (
            GroupeClasse.objects
            .filter(
                id=groupe_id
            )
            .first()
        )


    # ========================================================
    # ANNÉE SCOLAIRE
    # ========================================================

    annee_scolaire_obj = None

    if annee_id:

        annee_scolaire_obj = (
            AnneeScolaire.objects
            .filter(
                id=annee_id
            )
            .first()
        )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "ecoles":
            ecoles,

        "groupes":
            groupes,

        "annees_scolaires":
            annees_scolaires,

        "bulletins_annuels":
            bulletins_list,

        "groupe_id":
            groupe_id,

        "annee_scolaire_id":
            annee_id,

        "groupe_obj":
            groupe_obj,

        "annee_scolaire_obj":
            annee_scolaire_obj,
    }


    # ========================================================
    # RENDU
    # ========================================================

    return render(
        request,
        "bulletins/bulletins_annuel_classe.html",
        context
    )

# ============================================================
# AJAX : NIVEAUX PAR CYCLE
# ============================================================

def get_niveaux_par_cycle(request):

    cycle_id = request.GET.get(
        "cycle_id"
    )


    niveaux = (
        Niveau.objects
        .filter(
            cycle_id=cycle_id
        )
        .values(
            "id",
            "nom"
        )
    )


    return JsonResponse(
        list(niveaux),
        safe=False
    )


# ============================================================
# FIN
# ============================================================
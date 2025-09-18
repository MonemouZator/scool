from django.shortcuts import render, redirect
from django.contrib import messages
from eleve.models import Eleve
from niveau.models import Niveau
from groupe_classe.models import GroupeClasse
from annee_scolaire.models import AnneeScolaire
from note.models import Note
from .models import BulletinTrimestriel, BulletinAnnuel

from cycle.models import Cycle  # à importer
from groupe_classe.models import GroupeClasse  # déjà importé

# ------------------------
# BULLETINS TRIMESTRIELS PAR NIVEAU ET CYCLE
# ------------------------
def bulletins_trimestriels_niveau(request):
    cycles = Cycle.objects.all()
    niveaux = Niveau.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    cycle_id = request.GET.get('cycle')
    niveau_id = request.GET.get('niveau')
    annee_id = request.GET.get('annee_scolaire')
    trimestre = request.GET.get('trimestre')

    bulletins_list = []

    if niveau_id and annee_id and trimestre:
        eleves = Eleve.objects.filter(groupe_classe__niveau_id=niveau_id)
        if cycle_id:
            eleves = eleves.filter(groupe_classe__niveau__cycle_id=cycle_id)

        # Créer les bulletins et récupérer les moyennes
        for eleve in eleves:
            bulletin, created = BulletinTrimestriel.objects.get_or_create(
                eleve=eleve,
                trimestre=trimestre,
                annee_scolaire_id=annee_id
            )
            bulletins_list.append({
                'bulletin': bulletin,
                'notes': bulletin.notes_par_matiere,
                'moyenne_totale': bulletin.moyenne_totale or 0,
                'observation': bulletin.observation
            })

    for b in bulletins_list:
        # On récupère directement le rang formaté du modèle
        b['rang_formate'] = b['bulletin'].get_rang()

    # Tri par moyenne décroissante pour l'affichage
    bulletins_list.sort(key=lambda x: x['moyenne_totale'], reverse=True)

    context = {
        "cycles": cycles,
        "niveaux": niveaux,
        "annees_scolaires": annees_scolaires,
        "bulletins_trimestriels": bulletins_list,
        "cycle_id": cycle_id,
        "niveau_id": niveau_id,
        "annee_id": annee_id,
        "trimestre": trimestre,
        "cycle_obj": Cycle.objects.filter(id=cycle_id).first(),
        "niveau_obj": Niveau.objects.filter(id=niveau_id).first(),
        "annee_scolaire_obj": AnneeScolaire.objects.filter(id=annee_id).first(),
    }
    return render(request, "bulletins/bulletins_trimestriels_niveau.html", context)



# ------------------------
# BULLETINS TRIMESTRIELS PAR CLASSE
# ------------------------
def bulletins_trimestriels_classe(request):
    groupes_classes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')
    trimestre = request.GET.get('trimestre')

    bulletins_list = []

    if groupe_id and annee_id and trimestre:
        eleves = Eleve.objects.filter(groupe_classe_id=groupe_id)
        
        # Créer les bulletins trimestriels et récupérer les moyennes et observations
        for eleve in eleves:
            bulletin, created = BulletinTrimestriel.objects.get_or_create(
                eleve=eleve,
                trimestre=trimestre,
                annee_scolaire_id=annee_id
            )
            bulletins_list.append({
                'bulletin': bulletin,
                'notes': bulletin.notes_par_matiere,
                'moyenne_totale': bulletin.moyenne_totale or 0,
                'observation': bulletin.observation  # ← ajouté ici
            })

        # Tri décroissant par moyenne pour calculer les rangs
        bulletins_list.sort(key=lambda x: x['moyenne_totale'], reverse=True)

        rang = 0
        previous_moyenne = None
        ex_aequo_count = 0

        for index, b in enumerate(bulletins_list, start=1):
            moyenne = b['moyenne_totale']

            if moyenne == previous_moyenne:
                # même moyenne → ex æquo
                b['rang_formate'] = f"{rang}er Ex"
                ex_aequo_count += 1
            else:
                rang = index
                suffix = "er" if rang == 1 else "ème"
                b['rang_formate'] = f"{rang}{suffix}"
                ex_aequo_count = 0

            previous_moyenne = moyenne

    context = {
        'groupes_classes': groupes_classes,
        'annees_scolaires': annees_scolaires,
        'bulletins_trimestriels': bulletins_list,
        'groupe_id': groupe_id,
        'annee_id': annee_id,
        'trimestre': trimestre,
    }
    return render(request, "bulletins/bulletins_trimestriels_classe.html", context)


def resultat_trimestriel_classe(request):
    groupes_classes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')
    trimestre = request.GET.get('trimestre')

    bulletins_list = []
    groupe_obj = None
    annee_scolaire_obj = None
    trimestre_label = ""

    # Initialisation pour éviter UnboundLocalError
    eleves = Eleve.objects.none()

    statistiques = {
        'total_inscrits': 0,
        'ayant_composes': 0,
        'admis': 0,
        'non_admis': 0,
        'taux_reussite': 0,
        'taux_echec': 0,
        'filles_total': 0,
        'filles_composes': 0,
        'filles_admis': 0,
        'filles_non_admis': 0,
        'taux_filles_reussite': 0,
        'taux_filles_echec': 0,
    }

    if groupe_id and annee_id and trimestre:
        try:
            groupe_obj = GroupeClasse.objects.get(id=groupe_id)
        except GroupeClasse.DoesNotExist:
            groupe_obj = None

        try:
            annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee_scolaire_obj = None

        trimestre_label = f"Trimestre {trimestre}"

        bulletins = BulletinTrimestriel.objects.filter(
            eleve__groupe_classe_id=groupe_id,
            annee_scolaire_id=annee_id,
            trimestre=trimestre
        )

        # Préparer les bulletins avec moyenne et observation
        temp_list = [
            {
                'bulletin': b,
                'moyenne': b.moyenne_totale or 0,
                'observation': b.observation or "Non disponible"
            }
            for b in bulletins
        ]

        temp_list.sort(key=lambda x: x['moyenne'], reverse=True)

        # Calcul des rangs
        rang = 0
        previous_moyenne = None
        for index, b in enumerate(temp_list, start=1):
            if b['moyenne'] == previous_moyenne:
                b['rang'] = f"{rang}er Ex"
            else:
                rang = index
                b['rang'] = f"{rang}{'er' if rang == 1 else 'ème'}"
            previous_moyenne = b['moyenne']

        bulletins_list = temp_list

        # Statistiques
        eleves = Eleve.objects.filter(groupe_classe_id=groupe_id)
        statistiques['total_inscrits'] = eleves.count()
        statistiques['ayant_composes'] = len([b for b in bulletins_list if b['moyenne'] > 0])
        statistiques['admis'] = len([b for b in bulletins_list if b['moyenne'] >= 10])
        statistiques['non_admis'] = statistiques['ayant_composes'] - statistiques['admis']

        if statistiques['ayant_composes'] > 0:
            statistiques['taux_reussite'] = round(statistiques['admis'] / statistiques['ayant_composes'] * 100, 2)
            statistiques['taux_echec'] = round(statistiques['non_admis'] / statistiques['ayant_composes'] * 100, 2)

    # Statistiques filles
    filles = eleves.filter(genre__iexact="Femme")
    statistiques['filles_total'] = filles.count()
    statistiques['filles_composes'] = len([b for b in bulletins_list if b['bulletin'].eleve.genre.lower() == "femme" and b['moyenne'] > 0])
    statistiques['filles_admis'] = len([b for b in bulletins_list if b['bulletin'].eleve.genre.lower() == "femme" and b['moyenne'] >= 10])
    statistiques['filles_non_admis'] = statistiques['filles_composes'] - statistiques['filles_admis']

    if statistiques['filles_composes'] > 0:
        statistiques['taux_filles_reussite'] = round(statistiques['filles_admis'] / statistiques['filles_composes'] * 100, 2)
        statistiques['taux_filles_echec'] = round(statistiques['filles_non_admis'] / statistiques['filles_composes'] * 100, 2)
    else:
        statistiques['taux_filles_reussite'] = 0
        statistiques['taux_filles_echec'] = 0

    context = {
        'groupes_classes': groupes_classes,
        'annees_scolaires': annees_scolaires,
        'sorted_bulletins': bulletins_list,
        'groupe_id': groupe_id,
        'annee_id': annee_id,
        'trimestre': trimestre,
        'groupe_obj': groupe_obj,
        'annee_scolaire_obj': annee_scolaire_obj,
        'trimestre_label': trimestre_label,
        'statistiques': statistiques,
    }

    return render(request, "bulletins/resultat_trimestriel_classe.html", context)


# ------------------------
# RESULTATS ANNUELS PAR CLASSE
# ------------------------
from django.shortcuts import render
from .models import BulletinAnnuel
from eleve.models import Eleve, GroupeClasse
from annee_scolaire.models import AnneeScolaire

def resultat_annuel_classe(request):
    groupes_classes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')

    bulletins_list = []
    groupe_obj = None
    annee_scolaire_obj = None

    # Initialisation vide des statistiques
    statistiques = {
        'total_inscrits': 0,
        'ayant_composes': 0,
        'admis': 0,
        'non_admis': 0,
        'taux_reussite': 0,
        'taux_echec': 0,
        'filles_total': 0,
        'filles_composes': 0,
        'filles_admis': 0,
        'filles_non_admis': 0,
        'taux_filles_reussite': 0,
        'taux_filles_echec': 0,
    }

    # Définit eleves vide par défaut pour éviter UnboundLocalError
    eleves = Eleve.objects.none()

    if groupe_id and annee_id:
        # Récupération des objets
        try:
            groupe_obj = GroupeClasse.objects.get(id=groupe_id)
        except GroupeClasse.DoesNotExist:
            groupe_obj = None

        try:
            annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee_scolaire_obj = None

        # Bulletins
        bulletins = BulletinAnnuel.objects.filter(
            eleve__groupe_classe_id=groupe_id,
            annee_scolaire_id=annee_id
        )

        # Préparer la liste pour le template
        bulletins_list = [
            {
                'bulletin': b,
                'moyenne': b.moyenne_totale_annuelle or 0,
                'observation': b.observation_finale or "Non disponible"
            }
            for b in bulletins
        ]

        # Trier par moyenne décroissante
        bulletins_list.sort(key=lambda x: x['moyenne'], reverse=True)

        # Calcul des rangs
        rang = 0
        previous_moyenne = None
        for index, b in enumerate(bulletins_list, start=1):
            if b['moyenne'] == previous_moyenne:
                b['rang'] = f"{rang}er Ex"
            else:
                rang = index
                b['rang'] = f"{rang}{'er' if rang == 1 else 'ème'}"
            previous_moyenne = b['moyenne']

        # Liste des élèves pour les statistiques
        eleves = Eleve.objects.filter(groupe_classe_id=groupe_id)

    # ------------------------
    # Calcul des statistiques
    # ------------------------
    statistiques['total_inscrits'] = eleves.count()
    bulletins_composes = [b for b in bulletins_list if b['moyenne'] > 0]
    statistiques['ayant_composes'] = len(bulletins_composes)
    statistiques['admis'] = len([b for b in bulletins_composes if b['moyenne'] >= 10])
    statistiques['non_admis'] = statistiques['ayant_composes'] - statistiques['admis']

    if statistiques['ayant_composes']:
        statistiques['taux_reussite'] = round(statistiques['admis'] / statistiques['ayant_composes'] * 100, 2)
        statistiques['taux_echec'] = round(statistiques['non_admis'] / statistiques['ayant_composes'] * 100, 2)

    # Statistiques filles
    filles_total = [e for e in eleves if e.genre.lower() == "femme"]
    filles_composes = [b for b in bulletins_composes if b['bulletin'].eleve.genre.lower() == "femme"]
    filles_admis = [b for b in filles_composes if b['moyenne'] >= 10]

    statistiques['filles_total'] = len(filles_total)
    statistiques['filles_composes'] = len(filles_composes)
    statistiques['filles_admis'] = len(filles_admis)
    statistiques['filles_non_admis'] = len(filles_composes) - len(filles_admis)

    if statistiques['filles_composes']:
        statistiques['taux_filles_reussite'] = round(len(filles_admis) / len(filles_composes) * 100, 2)
        statistiques['taux_filles_echec'] = round(statistiques['filles_non_admis'] / len(filles_composes) * 100, 2)

    context = {
        'groupes_classes': groupes_classes,
        'annees_scolaires': annees_scolaires,
        'sorted_bulletins': bulletins_list,
        'groupe_id': groupe_id,
        'annee_id': annee_id,
        'groupe_obj': groupe_obj,
        'annee_scolaire_obj': annee_scolaire_obj,
        'statistiques': statistiques,
    }

    return render(request, "bulletins/resultat_annuel_classe.html", context)


# ------------------------
# VALIDATION BULLETINS
# ------------------------
def valider_bulletin_trimestre(request):
    if request.method == "POST":
        annee_id = request.POST.get('annee_scolaire')
        groupe_id = request.POST.get('groupe_classe')
        trimestre = request.POST.get('trimestre')

        eleves = Eleve.objects.filter(groupe_classe_id=groupe_id)
        for eleve in eleves:
            BulletinTrimestriel.objects.get_or_create(
                eleve=eleve,
                trimestre=trimestre,
                annee_scolaire_id=annee_id
            )
        messages.success(request, "Bulletins trimestriels validés.")
        return redirect('trimestre')

    return render(request, "bulletins/valider_bulletin_trimestre.html", {
        'groupes_classes': GroupeClasse.objects.all(),
        'annees_scolaires': AnneeScolaire.objects.all(),
    })


def valider_bulletin_annuel(request):
    if request.method == "POST":
        annee_id = request.POST.get('annee_scolaire')
        groupe_id = request.POST.get('groupe_classe')

        eleves = Eleve.objects.filter(groupe_classe_id=groupe_id)
        for eleve in eleves:
            BulletinAnnuel.objects.get_or_create(
                eleve=eleve,
                annee_scolaire_id=annee_id
            )
        messages.success(request, "Bulletins annuels validés.")
        return redirect('valider_bulletin')

    return render(request, "bulletins/valider_bulletin_annuel.html", {
        'groupes_classes': GroupeClasse.objects.all(),
        'annees_scolaires': AnneeScolaire.objects.all(),
    })


# ------------------------
# RESULTATS TRIMESTRIELS PAR NIVEAU
# ------------------------
from django.shortcuts import render
from eleve.models import Eleve, Niveau
from annee_scolaire.models import AnneeScolaire
from .models import BulletinTrimestriel

def resultats_trimestriels_niveau(request):
    niveaux = Niveau.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    niveau_id = request.GET.get('niveau')
    annee_id = request.GET.get('annee_scolaire')
    trimestre = request.GET.get('trimestre')

    bulletins_list = []
    niveau_obj = None
    annee_scolaire_obj = None
    trimestre_label = ""
    statistiques = {
        'total_inscrits': 0,
        'ayant_composes': 0,
        'admis': 0,
        'non_admis': 0,
        'taux_reussite': 0,
        'taux_echec': 0,
        'filles_total': 0,
        'filles_composes': 0,
        'filles_admis': 0,
        'filles_non_admis': 0,
        'taux_filles_reussite': 0,
        'taux_filles_echec': 0,
    }

    if niveau_id and annee_id and trimestre:
        # Objets pour affichage
        try:
            niveau_obj = Niveau.objects.get(id=niveau_id)
        except Niveau.DoesNotExist:
            niveau_obj = None

        try:
            annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee_scolaire_obj = None

        trimestre_label = f"Trimestre {trimestre}"

        # Récupération des élèves du niveau
        eleves = Eleve.objects.filter(groupe_classe__niveau_id=niveau_id)

        # Préparer les bulletins
        for eleve in eleves:
            bulletin, _ = BulletinTrimestriel.objects.get_or_create(
                eleve=eleve,
                trimestre=trimestre,
                annee_scolaire_id=annee_id
            )
            bulletins_list.append({
                'bulletin': bulletin,
                'moyenne': bulletin.moyenne_totale or 0,
                'observation': bulletin.observation or "Non disponible"
            })

        # Trier par moyenne décroissante
        bulletins_list.sort(key=lambda x: x['moyenne'], reverse=True)

        # Calcul des rangs avec ex æquo
        rang = 0
        previous_moyenne = None
        for index, b in enumerate(bulletins_list, start=1):
            if b['moyenne'] == previous_moyenne:
                b['rang'] = f"{rang}er Ex"
            else:
                rang = index
                b['rang'] = f"{rang}{'er' if rang == 1 else 'ème'}"
            previous_moyenne = b['moyenne']

        # ------------------------
        # Calcul des statistiques globales
        # ------------------------
        statistiques['total_inscrits'] = eleves.count()
        bulletins_composes = [b for b in bulletins_list if b['moyenne'] > 0]
        statistiques['ayant_composes'] = len(bulletins_composes)
        statistiques['admis'] = len([b for b in bulletins_composes if b['moyenne'] >= 10])
        statistiques['non_admis'] = statistiques['ayant_composes'] - statistiques['admis']

        # Taux global
        if statistiques['ayant_composes'] > 0:
            statistiques['taux_reussite'] = round(statistiques['admis'] / statistiques['ayant_composes'] * 100, 2)
            statistiques['taux_echec'] = round(statistiques['non_admis'] / statistiques['ayant_composes'] * 100, 2)

        # Statistiques filles
        filles = [b for b in bulletins_composes if b['bulletin'].eleve.genre.lower() == "femme"]
        statistiques['filles_total'] = len([e for e in eleves if e.genre.lower() == "femme"])
        statistiques['filles_composes'] = len(filles)
        statistiques['filles_admis'] = len([b for b in filles if b['moyenne'] >= 10])
        statistiques['filles_non_admis'] = statistiques['filles_composes'] - statistiques['filles_admis']

        # Taux filles
        if statistiques['filles_composes'] > 0:
            statistiques['taux_filles_reussite'] = round(statistiques['filles_admis'] / statistiques['filles_composes'] * 100, 2)
            statistiques['taux_filles_echec'] = round(statistiques['filles_non_admis'] / statistiques['filles_composes'] * 100, 2)

    context = {
        'niveaux': niveaux,
        'annees_scolaires': annees_scolaires,
        'sorted_bulletins': bulletins_list,
        'niveau_id': niveau_id,
        'annee_id': annee_id,
        'trimestre': trimestre,
        'niveau_obj': niveau_obj,
        'annee_scolaire_obj': annee_scolaire_obj,
        'trimestre_label': trimestre_label,
        'statistiques': statistiques,
    }

    return render(request, "bulletins/resultats_trimestriels_niveau.html", context)



def resultats_annuels_niveau(request):
    niveaux = Niveau.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    niveau_id = request.GET.get('niveau')
    annee_id = request.GET.get('annee_scolaire')

    bulletins_list = []
    niveau_obj = None
    annee_scolaire_obj = None

    statistiques = {
        'total_inscrits': 0,
        'ayant_composes': 0,
        'admis': 0,
        'non_admis': 0,
        'taux_reussite': 0,
        'taux_echec': 0,
        'filles_total': 0,
        'filles_composes': 0,
        'filles_admis': 0,
        'filles_non_admis': 0,
        'taux_filles_reussite': 0,
        'taux_filles_echec': 0,
    }

    if niveau_id and annee_id:
        # Récupération des objets
        try:
            niveau_obj = Niveau.objects.get(id=niveau_id)
        except Niveau.DoesNotExist:
            niveau_obj = None

        try:
            annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee_scolaire_obj = None

        # Récupération des élèves
        eleves = Eleve.objects.filter(groupe_classe__niveau_id=niveau_id)

        # Création ou récupération des bulletins annuels
        for eleve in eleves:
            bulletin, _ = BulletinAnnuel.objects.get_or_create(
                eleve=eleve,
                annee_scolaire_id=annee_id
            )
            bulletins_list.append({
                'bulletin': bulletin,
                'moyenne_totale': bulletin.moyenne_totale_annuelle or 0,
                'observation': bulletin.observation_finale or "Non disponible"
            })

        # Trier par moyenne décroissante
        bulletins_list.sort(key=lambda x: x['moyenne_totale'], reverse=True)

        # Calcul des rangs avec gestion des ex æquo
        rang = 0
        previous_moyenne = None
        for index, b in enumerate(bulletins_list, start=1):
            if b['moyenne_totale'] == previous_moyenne:
                b['rang'] = f"{rang}er Ex"
            else:
                rang = index
                b['rang'] = f"{rang}{'er' if rang == 1 else 'ème'}"
            previous_moyenne = b['moyenne_totale']

        # ------------------------
        # Calcul des statistiques globales
        # ------------------------
        statistiques['total_inscrits'] = eleves.count()
        bulletins_composes = [b for b in bulletins_list if b['moyenne_totale'] > 0]
        statistiques['ayant_composes'] = len(bulletins_composes)
        statistiques['admis'] = len([b for b in bulletins_composes if b['moyenne_totale'] >= 10])
        statistiques['non_admis'] = statistiques['ayant_composes'] - statistiques['admis']

        # Taux global
        if statistiques['ayant_composes']:
            statistiques['taux_reussite'] = round(statistiques['admis'] / statistiques['ayant_composes'] * 100, 2)
            statistiques['taux_echec'] = round(statistiques['non_admis'] / statistiques['ayant_composes'] * 100, 2)

        # Statistiques filles
        filles = [b for b in bulletins_composes if b['bulletin'].eleve.genre.lower() == "femme"]
        statistiques['filles_total'] = len([e for e in eleves if e.genre.lower() == "femme"])
        statistiques['filles_composes'] = len(filles)
        statistiques['filles_admis'] = len([b for b in filles if b['moyenne_totale'] >= 10])
        statistiques['filles_non_admis'] = statistiques['filles_composes'] - statistiques['filles_admis']

        # Taux filles
        if statistiques['filles_composes']:
            statistiques['taux_filles_reussite'] = round(statistiques['filles_admis'] / statistiques['filles_composes'] * 100, 2)
            statistiques['taux_filles_echec'] = round(statistiques['filles_non_admis'] / statistiques['filles_composes'] * 100, 2)

    context = {
        'niveaux': niveaux,
        'annees_scolaires': annees_scolaires,
        'bulletins': bulletins_list,
        'niveau_selectionne': int(niveau_id) if niveau_id else None,
        'annee_scolaire_selectionnee': int(annee_id) if annee_id else None,
        'niveau_obj': niveau_obj,
        'annee_scolaire_obj': annee_scolaire_obj,
        'statistiques': statistiques,
    }

    return render(request, "bulletins/resultats_annuels_niveau.html", context)

from django.db.models import Avg


def bulletins_annuels_classe(request):
    annee_id = request.GET.get("annee")
    groupe_id = request.GET.get("groupe")

    eleves = Eleve.objects.all()
    if annee_id:
        eleves = eleves.filter(annee_scolaire_id=annee_id)
    if groupe_id:
        eleves = eleves.filter(groupeclasse_id=groupe_id)

    bulletins_annuels = []

    for eleve in eleves:
        # Moyennes par trimestre
        moyennes_trimestrielles = []
        for trimestre in [1, 2, 3]:
            moyenne_trim = (
                Note.objects.filter(
                    eleve=eleve,
                    trimestre=trimestre,
                    annee_scolaire_id=annee_id
                )
                .values("matiere__nom")
                .annotate(moyenne_matiere=Avg("valeur"))
                .aggregate(m=Avg("moyenne_matiere"))["m"]
            )
            moyennes_trimestrielles.append(moyenne_trim if moyenne_trim else 0)

        # Moyenne annuelle = moyenne des 3 trimestres
        moyenne_annuelle = sum(moyennes_trimestrielles) / 3 if moyennes_trimestrielles else 0

        # Observation
        observation = "Médiocre"
        if moyenne_annuelle >= 16:
            observation = "Excellent"
        elif moyenne_annuelle >= 14:
            observation = "Très Bien"
        elif moyenne_annuelle >= 12:
            observation = "Bien"
        elif moyenne_annuelle >= 10:
            observation = "Passable"
        else:
            observation = "Insuffisant"

        bulletins_annuels.append({
            "eleve": eleve,
            "moyennes_trimestrielles": moyennes_trimestrielles,
            "moyenne_annuelle": round(moyenne_annuelle, 2),
            "observation": observation,
        })

    # Classement (par moyenne annuelle décroissante)
    bulletins_annuels.sort(key=lambda x: x["moyenne_annuelle"], reverse=True)
    for i, b in enumerate(bulletins_annuels, start=1):
        b["rang"] = i

    context = {
        "bulletins_annuels": bulletins_annuels,
        "annee_scolaire": AnneeScolaire.objects.filter(id=annee_id).first(),
        "groupe": GroupeClasse.objects.filter(id=groupe_id).first(),
    }
    return render(request, "bulletins/bulletins_annuel_classe.html", context)


from django.db.models import Avg, F

from django.shortcuts import render
from django.db.models import Avg, F
from eleve.models import Eleve
from annee_scolaire.models import AnneeScolaire
from note.models import Note
from bulletin.models import BulletinAnnuel


from django.shortcuts import render
from eleve.models import Eleve
from annee_scolaire.models import AnneeScolaire
from note.models import Note
from bulletin.models import BulletinAnnuel
from niveau.models import Niveau
from cycle.models import Cycle
from django.db.models import Avg, F

def bulletins_annuels_niveau(request):
    # Récupération des filtres
    cycles = Cycle.objects.all()
    niveaux = Niveau.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    cycle_id = request.GET.get('cycle')
    niveau_id = request.GET.get('niveau')
    annee_id = request.GET.get('annee_scolaire')

    bulletins_list = []

    if niveau_id and annee_id:
        eleves = Eleve.objects.filter(groupe_classe__niveau_id=niveau_id)
        if cycle_id:
            eleves = eleves.filter(groupe_classe__niveau__cycle_id=cycle_id)

        # Génération ou récupération des bulletins
        for eleve in eleves:
            bulletin, created = BulletinAnnuel.objects.get_or_create(
                eleve=eleve,
                annee_scolaire_id=annee_id
            )

            # Calcul des moyennes trimestrielles
            moyennes_trimestrielles = []
            for t in range(1, 4):
                moy = Note.objects.filter(
                    eleve=eleve,
                    annee_scolaire_id=annee_id,
                    trimestre=t
                ).aggregate(moy=Avg(F('note_cours') + F('note_comp')))['moy'] or 0
                moyennes_trimestrielles.append(round(moy / 2, 2))

            bulletins_list.append({
                'eleve': eleve,
                'bulletin': bulletin,
                'moyennes_trimestrielles': moyennes_trimestrielles,
                'moyenne_annuelle': bulletin.moyenne_totale_annuelle,
                'observation': bulletin.observation_finale,
            })

        # Gestion des rangs avec ex æquo
        bulletins_list.sort(key=lambda x: x['moyenne_annuelle'], reverse=True)
        rang = 0
        previous_moy = None
        compteur_exoquo = 0
        for index, b in enumerate(bulletins_list, start=1):
            if b['moyenne_annuelle'] == previous_moy:
                b['rang'] = f"{rang} Ex"
                compteur_exoquo += 1
            else:
                rang = index
                b['rang'] = f"{rang}{'er' if rang == 1 else 'ème'}"
                compteur_exoquo = 0
            previous_moy = b['moyenne_annuelle']

    context = {
        "cycles": cycles,
        "niveaux": niveaux,
        "annees_scolaires": annees_scolaires,
        "bulletins_annuels": bulletins_list,
        "cycle_id": cycle_id,
        "niveau_id": niveau_id,
        "annee_scolaire_id": annee_id,
        "cycle_obj": Cycle.objects.filter(id=cycle_id).first(),
        "niveau_obj": Niveau.objects.filter(id=niveau_id).first(),
        "annee_scolaire_obj": AnneeScolaire.objects.filter(id=annee_id).first(),
    }


    return render(request, "bulletins/bulletins_annuel_niveau.html", context)


from django.http import JsonResponse

def get_niveaux_par_cycle(request):
    cycle_id = request.GET.get('cycle_id')
    niveaux = Niveau.objects.filter(cycle_id=cycle_id).values('id', 'nom')
    return JsonResponse(list(niveaux), safe=False)


def bulletins_annuels_classe(request):
    # Récupérer les filtres
    groupes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get('groupe')
    annee_id = request.GET.get('annee_scolaire')

    bulletins_list = []

    if groupe_id and annee_id:
        eleves = Eleve.objects.filter(groupe_classe_id=groupe_id)

        # Génération ou récupération des bulletins pour chaque élève
        for eleve in eleves:
            bulletin, created = BulletinAnnuel.objects.get_or_create(
                eleve=eleve,
                annee_scolaire_id=annee_id
            )

            # Calcul des moyennes trimestrielles
            moyennes_trimestrielles = []
            for t in range(1, 4):
                moy = Note.objects.filter(
                    eleve=eleve,
                    annee_scolaire_id=annee_id,
                    trimestre=t
                ).aggregate(moy=Avg(F('note_cours') + F('note_comp')))['moy'] or 0
                moyennes_trimestrielles.append(round(moy / 2, 2))

            bulletins_list.append({
                'eleve': eleve,
                'bulletin': bulletin,
                'moyennes_trimestrielles': moyennes_trimestrielles,
                'moyenne_annuelle': bulletin.moyenne_totale_annuelle,
                'observation': bulletin.observation_finale,
            })

        # Calcul des rangs avec gestion des ex-aequo
        bulletins_list.sort(key=lambda x: x['moyenne_annuelle'], reverse=True)
        rang = 0
        previous_moy = None
        for index, b in enumerate(bulletins_list, start=1):
            if b['moyenne_annuelle'] == previous_moy:
                b['rang'] = f"{rang} Ex"
            else:
                rang = index
                b['rang'] = f"{rang}{'er' if rang == 1 else 'ème'}"
            previous_moy = b['moyenne_annuelle']

    context = {
        "groupes": groupes,
        "annees_scolaires": annees_scolaires,
        "bulletins_annuels": bulletins_list,
        "groupe_id": groupe_id,
        "annee_scolaire_id": annee_id,
        "groupe_obj": GroupeClasse.objects.filter(id=groupe_id).first(),
        "annee_scolaire_obj": AnneeScolaire.objects.filter(id=annee_id).first(),
    }

    return render(request, "bulletins/bulletins_annuel_classe.html", context)

from django.shortcuts import render, redirect
from django.contrib import messages
from eleve.models import Eleve
from niveau.models import Niveau
from groupe_classe.models import GroupeClasse
from annee_scolaire.models import AnneeScolaire
from note.models import Note
from .models import BulletinTrimestriel, BulletinAnnuel

from cycle.models import Cycle , Etablissement # à importer
from groupe_classe.models import GroupeClasse  # déjà importé

# ------------------------
# BULLETINS TRIMESTRIELS PAR NIVEAU ET CYCLE
# ------------------------
def bulletins_trimestriels_niveau(request):
    ecoles=Etablissement.objects.all()
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
        "ecoles":ecoles,
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
    ecoles=Etablissement.objects.all()
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
        "ecoles":ecoles,
    }
    return render(request, "bulletins/bulletins_trimestriels_classe.html", context)


def resultat_trimestriel_classe(request):
    ecoles = Etablissement.objects.all()
    groupes_classes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')
    trimestre = request.GET.get('trimestre')

    bulletins_list = []
    groupe_obj = None
    annee_scolaire_obj = None
    trimestre_label = ""
    eleves = Eleve.objects.none()  # pour éviter UnboundLocalError

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

        # Déterminer le cycle pour ajuster la moyenne
        max_note = 20
        seuil_admission = 10
        if groupe_obj and hasattr(groupe_obj.niveau, 'cycle') and groupe_obj.niveau.cycle:
            cycle = groupe_obj.niveau.cycle
            if cycle.nom.lower() == "primaire":
                max_note = 10
                seuil_admission = 5
            else:
                max_note = 20
                seuil_admission = 10

        # Préparer les bulletins avec moyenne ajustée et observation
        temp_list = [
            {
                'bulletin': b,
                'moyenne': (b.moyenne_totale or 0),
                'observation': b.observation or "Non disponible"
            }
            for b in bulletins
        ]

        # Trier par moyenne décroissante
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

        # Récupérer les élèves
        eleves = Eleve.objects.filter(groupe_classe_id=groupe_id)

        # Statistiques globales
        statistiques['total_inscrits'] = eleves.count()
        statistiques['ayant_composes'] = len([b for b in bulletins_list if b['moyenne'] > 0])
        statistiques['admis'] = len([b for b in bulletins_list if b['moyenne'] >= seuil_admission])
        statistiques['non_admis'] = statistiques['ayant_composes'] - statistiques['admis']

        if statistiques['ayant_composes'] > 0:
            statistiques['taux_reussite'] = round(statistiques['admis'] / statistiques['ayant_composes'] * 100, 2)
            statistiques['taux_echec'] = round(statistiques['non_admis'] / statistiques['ayant_composes'] * 100, 2)

        # Statistiques filles
        filles = eleves.filter(genre__iexact="Femme")
        statistiques['filles_total'] = filles.count()
        statistiques['filles_composes'] = len([
            b for b in bulletins_list 
            if b['bulletin'].eleve.genre.lower() == "femme" and b['moyenne'] > 0
        ])
        statistiques['filles_admis'] = len([
            b for b in bulletins_list 
            if b['bulletin'].eleve.genre.lower() == "femme" and b['moyenne'] >= seuil_admission
        ])
        statistiques['filles_non_admis'] = statistiques['filles_composes'] - statistiques['filles_admis']

        if statistiques['filles_composes'] > 0:
            statistiques['taux_filles_reussite'] = round(statistiques['filles_admis'] / statistiques['filles_composes'] * 100, 2)
            statistiques['taux_filles_echec'] = round(statistiques['filles_non_admis'] / statistiques['filles_composes'] * 100, 2)

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
        "ecoles": ecoles,
    }

    return render(request, "bulletins/resultat_trimestriel_classe.html", context)


# ------------------------
# RESULTATS ANNUELS PAR CLASSE
# ------------------------

def resultat_annuel_classe(request):
    ecoles = Etablissement.objects.all()
    groupes_classes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')

    bulletins_list = []
    groupe_obj = None
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

    eleves = Eleve.objects.none()  # sécurité

    if groupe_id and annee_id:
        groupe_obj = GroupeClasse.objects.filter(id=groupe_id).first()
        annee_scolaire_obj = AnneeScolaire.objects.filter(id=annee_id).first()

        # 🔹 Déterminer le seuil selon le cycle
        seuil_admission = 10
        if groupe_obj and groupe_obj.niveau.cycle and groupe_obj.niveau.cycle.nom.lower() == "primaire":
            seuil_admission = 5

        # 🔹 Récupérer les bulletins annuels existants
        bulletins = BulletinAnnuel.objects.filter(
            eleve__groupe_classe_id=groupe_id,
            annee_scolaire_id=annee_id
        )

        # 🔹 Préparer la liste pour le template
        bulletins_list = [
            {
                'bulletin': b,
                'moyenne': b.moyenne_totale_annuelle or 0,
                'observation': b.observation_finale or "Non disponible"
            }
            for b in bulletins
        ]

        # 🔹 Trier par moyenne décroissante
        bulletins_list.sort(key=lambda x: x['moyenne'], reverse=True)

        # 🔹 Calcul des rangs
        rang = 0
        previous_moyenne = None
        for index, b in enumerate(bulletins_list, start=1):
            if b['moyenne'] == previous_moyenne:
                b['rang'] = f"{rang}er Ex"
            else:
                rang = index
                b['rang'] = f"{rang}{'er' if rang == 1 else 'ème'}"
            previous_moyenne = b['moyenne']

        # 🔹 Liste des élèves
        eleves = Eleve.objects.filter(groupe_classe_id=groupe_id)

        # ================= STATISTIQUES =================
        statistiques['total_inscrits'] = eleves.count()

        bulletins_composes = [b for b in bulletins_list if b['moyenne'] > 0]
        statistiques['ayant_composes'] = len(bulletins_composes)
        statistiques['admis'] = len([b for b in bulletins_composes if b['moyenne'] >= seuil_admission])
        statistiques['non_admis'] = statistiques['ayant_composes'] - statistiques['admis']

        if statistiques['ayant_composes'] > 0:
            statistiques['taux_reussite'] = round(statistiques['admis'] / statistiques['ayant_composes'] * 100, 2)
            statistiques['taux_echec'] = round(statistiques['non_admis'] / statistiques['ayant_composes'] * 100, 2)

        # ================= STATISTIQUES FILLES =================
        filles = [e for e in eleves if e.genre.lower() == "femme"]
        statistiques['filles_total'] = len(filles)

        filles_composes = [b for b in bulletins_composes if b['bulletin'].eleve.genre.lower() == "femme"]
        statistiques['filles_composes'] = len(filles_composes)
        filles_admis = [b for b in filles_composes if b['moyenne'] >= seuil_admission]
        statistiques['filles_admis'] = len(filles_admis)
        statistiques['filles_non_admis'] = len(filles_composes) - len(filles_admis)

        if statistiques['filles_composes'] > 0:
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
        "ecoles": ecoles,
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
    ecoles = Etablissement.objects.all()
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

    stats_par_cycle = []

    if niveau_id and annee_id and trimestre:
        niveau_obj = Niveau.objects.filter(id=niveau_id).first()
        annee_scolaire_obj = AnneeScolaire.objects.filter(id=annee_id).first()
        trimestre_label = f"Trimestre {trimestre}"

        # 🔹 Déterminer le seuil selon le cycle
        seuil_admission = 10
        if niveau_obj and niveau_obj.cycle and niveau_obj.cycle.nom.lower() == "primaire":
            seuil_admission = 5

        # 🔹 Élèves du niveau
        eleves = Eleve.objects.filter(groupe_classe__niveau=niveau_obj)

        # 🔹 Bulletins existants uniquement
        bulletins = BulletinTrimestriel.objects.filter(
            eleve__in=eleves,
            trimestre=trimestre,
            annee_scolaire_id=annee_id
        )

        # 🔹 Préparation des bulletins
        for b in bulletins:
            bulletins_list.append({
                'bulletin': b,
                'moyenne': b.moyenne_totale or 0,
                'observation': b.observation or "Non disponible"
            })

        # 🔹 Classement
        bulletins_list.sort(key=lambda x: x['moyenne'], reverse=True)

        rang = 0
        previous_moyenne = None
        for index, b in enumerate(bulletins_list, start=1):
            if b['moyenne'] == previous_moyenne:
                b['rang'] = f"{rang}er Ex"
            else:
                rang = index
                b['rang'] = f"{rang}{'er' if rang == 1 else 'ème'}"
            previous_moyenne = b['moyenne']

        # ================= STATISTIQUES =================
        statistiques['total_inscrits'] = eleves.count()

        composés = [b for b in bulletins_list if b['moyenne'] > 0]
        statistiques['ayant_composes'] = len(composés)

        statistiques['admis'] = len([b for b in composés if b['moyenne'] >= seuil_admission])
        statistiques['non_admis'] = statistiques['ayant_composes'] - statistiques['admis']

        if statistiques['ayant_composes'] > 0:
            statistiques['taux_reussite'] = round(statistiques['admis'] / statistiques['ayant_composes'] * 100, 2)
            statistiques['taux_echec'] = round(statistiques['non_admis'] / statistiques['ayant_composes'] * 100, 2)

        # ================= STATISTIQUES FILLES =================
        filles = eleves.filter(genre__iexact="femme")
        statistiques['filles_total'] = filles.count()

        filles_composées = [
            b for b in composés if b['bulletin'].eleve.genre.lower() == "femme"
        ]
        statistiques['filles_composes'] = len(filles_composées)

        statistiques['filles_admis'] = len([
            b for b in filles_composées if b['moyenne'] >= seuil_admission
        ])
        statistiques['filles_non_admis'] = statistiques['filles_composes'] - statistiques['filles_admis']

        if statistiques['filles_composes'] > 0:
            statistiques['taux_filles_reussite'] = round(
                statistiques['filles_admis'] / statistiques['filles_composes'] * 100, 2
            )
            statistiques['taux_filles_echec'] = round(
                statistiques['filles_non_admis'] / statistiques['filles_composes'] * 100, 2
            )

        # ================= STATISTIQUES PAR CYCLE =================
        for cycle in Cycle.objects.all():
            eleves_cycle = Eleve.objects.filter(
                groupe_classe__niveau__cycle=cycle,
                groupe_classe__niveau=niveau_obj
            )

            bulletins_cycle = BulletinTrimestriel.objects.filter(
                eleve__in=eleves_cycle,
                trimestre=trimestre,
                annee_scolaire_id=annee_id
            )

            seuil_cycle = 5 if cycle.nom.lower() == "primaire" else 10
            composés_cycle = [b for b in bulletins_cycle if b.moyenne_totale and b.moyenne_totale > 0]
            admis_cycle = [b for b in composés_cycle if b.moyenne_totale >= seuil_cycle]

            stats_par_cycle.append({
                'cycle': cycle.nom,
                'total': eleves_cycle.count(),
                'ayant_composes': len(composés_cycle),
                'admis': len(admis_cycle),
                'taux_reussite': round(len(admis_cycle) / len(composés_cycle) * 100, 2)
                if composés_cycle else 0
            })

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
        'stats_par_cycle': stats_par_cycle,
        'ecoles': ecoles,
    }

    return render(request, "bulletins/resultats_trimestriels_niveau.html", context)



def resultats_annuels_niveau(request):
    ecoles = Etablissement.objects.all()
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
        niveau_obj = Niveau.objects.filter(id=niveau_id).first()
        annee_scolaire_obj = AnneeScolaire.objects.filter(id=annee_id).first()

        # Récupérer tous les élèves du niveau
        eleves = Eleve.objects.filter(groupe_classe__niveau_id=niveau_id)

        # Déterminer le seuil d’admission selon le cycle
        seuil_admission = 10
        if niveau_obj and hasattr(niveau_obj, 'cycle') and niveau_obj.cycle:
            if niveau_obj.cycle.nom.lower() == "primaire":
                seuil_admission = 5

        # Récupérer ou créer les bulletins annuels
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

        # ================= STATISTIQUES =================
        statistiques['total_inscrits'] = eleves.count()
        bulletins_composes = [b for b in bulletins_list if b['moyenne_totale'] > 0]
        statistiques['ayant_composes'] = len(bulletins_composes)
        statistiques['admis'] = len([b for b in bulletins_composes if b['moyenne_totale'] >= seuil_admission])
        statistiques['non_admis'] = statistiques['ayant_composes'] - statistiques['admis']

        if statistiques['ayant_composes'] > 0:
            statistiques['taux_reussite'] = round(statistiques['admis'] / statistiques['ayant_composes'] * 100, 2)
            statistiques['taux_echec'] = round(statistiques['non_admis'] / statistiques['ayant_composes'] * 100, 2)

        # ================= STATISTIQUES FILLES =================
        filles = [e for e in eleves if e.genre.lower() == "femme"]
        statistiques['filles_total'] = len(filles)
        filles_composes = [b for b in bulletins_composes if b['bulletin'].eleve.genre.lower() == "femme"]
        statistiques['filles_composes'] = len(filles_composes)
        filles_admis = [b for b in filles_composes if b['moyenne_totale'] >= seuil_admission]
        statistiques['filles_admis'] = len(filles_admis)
        statistiques['filles_non_admis'] = len(filles_composes) - len(filles_admis)

        if statistiques['filles_composes'] > 0:
            statistiques['taux_filles_reussite'] = round(len(filles_admis) / len(filles_composes) * 100, 2)
            statistiques['taux_filles_echec'] = round(statistiques['filles_non_admis'] / len(filles_composes) * 100, 2)

    context = {
        'niveaux': niveaux,
        'annees_scolaires': annees_scolaires,
        'bulletins': bulletins_list,
        'niveau_selectionne': int(niveau_id) if niveau_id else None,
        'annee_scolaire_selectionnee': int(annee_id) if annee_id else None,
        'niveau_obj': niveau_obj,
        'annee_scolaire_obj': annee_scolaire_obj,
        'statistiques': statistiques,
        'ecoles': ecoles,
    }

    return render(request, "bulletins/resultats_annuels_niveau.html", context)

from django.db.models import Avg


def bulletins_annuels_classe(request):
    ecoles=Etablissement.objects.all()
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
        "ecoles":ecoles,
    }
    return render(request, "bulletins/bulletins_annuel_classe.html", context)


from django.db.models import Avg, F

def bulletins_annuels_niveau(request):
    
    # Récupération des filtres
    cycles = Cycle.objects.all()
    niveaux = Niveau.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()
    ecoles=Etablissement.objects.all()
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
        "ecoles":ecoles,
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
    ecoles=Etablissement.objects.all()
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
        "ecoles":ecoles,
        "groupes": groupes,
        "annees_scolaires": annees_scolaires,
        "bulletins_annuels": bulletins_list,
        "groupe_id": groupe_id,
        "annee_scolaire_id": annee_id,
        "groupe_obj": GroupeClasse.objects.filter(id=groupe_id).first(),
        "annee_scolaire_obj": AnneeScolaire.objects.filter(id=annee_id).first(),
    }

    return render(request, "bulletins/bulletins_annuel_classe.html", context)


###################################################################
#LES DROIT DU FONDATEUR
# #################################################################


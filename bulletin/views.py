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


# ------------------------
# RESULTATS TRIMESTRIELS PAR CLASSE
# ------------------------
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
            {'bulletin': b, 'moyenne': b.moyenne_totale or 0, 'observation': b.observation or "Non disponible"}
            for b in bulletins
        ]

        # Trier par moyenne décroissante
        temp_list.sort(key=lambda x: x['moyenne'], reverse=True)

        # Calcul des rangs avec ex æquo
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
    }

    return render(request, "bulletins/resultat_trimestriel_classe.html", context)

# ------------------------
# RESULTATS ANNUELS PAR CLASSE
# ------------------------
from django.shortcuts import render
from .models import BulletinAnnuel
from eleve.models import GroupeClasse
from annee_scolaire.models import AnneeScolaire

def resultat_annuel_classe(request):
    groupes_classes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')

    bulletins_list = []
    groupe_obj = None
    annee_scolaire_obj = None

    if groupe_id and annee_id:
        # Récupération des objets pour affichage dans le template
        try:
            groupe_obj = GroupeClasse.objects.get(id=groupe_id)
        except GroupeClasse.DoesNotExist:
            groupe_obj = None

        try:
            annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee_scolaire_obj = None

        # Récupération des bulletins
        bulletins = BulletinAnnuel.objects.filter(
            eleve__groupe_classe_id=groupe_id,
            annee_scolaire_id=annee_id
        )

        # Préparer les bulletins avec moyenne et observation
        temp_list = [
            {
                'bulletin': b,
                'moyenne': b.moyenne_totale_annuelle or 0,
                'observation': b.observation_finale or "Non disponible"
            }
            for b in bulletins
        ]

        # Trier par moyenne décroissante
        temp_list.sort(key=lambda x: x['moyenne'], reverse=True)

        # Calcul des rangs avec gestion des ex æquo
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

    context = {
        'groupes_classes': groupes_classes,
        'annees_scolaires': annees_scolaires,
        'sorted_bulletins': bulletins_list,  # pour correspondre au template
        'groupe_id': groupe_id,
        'annee_id': annee_id,
        'groupe_obj': groupe_obj,
        'annee_scolaire_obj': annee_scolaire_obj,
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

    if niveau_id and annee_id and trimestre:
        try:
            niveau_obj = Niveau.objects.get(id=niveau_id)
        except Niveau.DoesNotExist:
            niveau_obj = None

        try:
            annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee_scolaire_obj = None

        trimestre_label = f"Trimestre {trimestre}"

        eleves = Eleve.objects.filter(groupe_classe__niveau_id=niveau_id)
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

    context = {
        'niveaux': niveaux,
        'annees_scolaires': annees_scolaires,
        'sorted_bulletins': bulletins_list,  # pour le template
        'niveau_id': niveau_id,
        'annee_id': annee_id,
        'trimestre': trimestre,
        'niveau_obj': niveau_obj,
        'annee_scolaire_obj': annee_scolaire_obj,
        'trimestre_label': trimestre_label,
    }

    return render(request, "bulletins/resultats_trimestriels_niveau.html", context)


# ------------------------
# RESULTATS ANNUELS PAR NIVEAU
# ------------------------
def resultats_annuels_niveau(request):
    niveaux = Niveau.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    niveau_id = request.GET.get('niveau')
    annee_id = request.GET.get('annee_scolaire')

    bulletins_list = []
    niveau_obj = None
    annee_scolaire_obj = None

    if niveau_id and annee_id:
        try:
            niveau_obj = Niveau.objects.get(id=niveau_id)
        except Niveau.DoesNotExist:
            niveau_obj = None

        try:
            annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee_scolaire_obj = None

        eleves = Eleve.objects.filter(groupe_classe__niveau_id=niveau_id)
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

        # Calcul des rangs avec ex æquo
        rang = 0
        previous_moyenne = None
        for index, b in enumerate(bulletins_list, start=1):
            if b['moyenne_totale'] == previous_moyenne:
                b['rang'] = f"{rang}er Ex"
            else:
                rang = index
                b['rang'] = f"{rang}{'er' if rang == 1 else 'ème'}"
            previous_moyenne = b['moyenne_totale']

    context = {
        'niveaux': niveaux,
        'annees_scolaires': annees_scolaires,
        'bulletins': bulletins_list,  # pour le template
        'niveau_id': niveau_id,
        'annee_id': annee_id,
        'niveau_obj': niveau_obj,
        'annee_scolaire_obj': annee_scolaire_obj,
    }

    return render(request, "bulletins/resultats_annuels_niveau.html", context)

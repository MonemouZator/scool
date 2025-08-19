from django.shortcuts import render
from bulletin.models import BulletinTrimestriel,BulletinAnnuel
from annee_scolaire.models import AnneeScolaire
from niveau.models import Niveau
from groupe_classe.models import GroupeClasse
from django.db.models import Avg,F
from eleve.models import Eleve
from note.models import Note
from django.shortcuts import render, redirect
from django.contrib import messages

def format_rang(rang):
    """
    Cette fonction formate le rang avec un suffixe ordinal.
    Par exemple : 1 -> 1er, 2 -> 2ème, 3 -> 3ème, etc.
    """
    if 10 <= rang % 100 <= 20:
        suffix = 'ème'  # Cas spécial pour les nombres entre 11 et 20
    else:
        suffixes = {1: 'er', 2: 'ème', 3: 'ème'}
        suffix = suffixes.get(rang % 10, 'ème')
    
    return f"{rang}{suffix}"

def bulletins_trimestriels_niveau(request):
    niveaux = Niveau.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    niveau_ids = request.GET.getlist('niveau')  # supporte un ou plusieurs niveaux
    annee_scolaire_id = request.GET.get('annee_scolaire')
    trimestre = request.GET.get('trimestre')

    notes = Note.objects.all()

    # ✅ Correction ici : on filtre par eleve__groupe_classe__niveau_id
    if niveau_ids:
        notes = notes.filter(eleve__groupe_classe__niveau_id__in=niveau_ids)
    if annee_scolaire_id:
        notes = notes.filter(annee_scolaire_id=annee_scolaire_id)
    if trimestre:
        notes = notes.filter(trimestre=trimestre)

    if not notes.exists():
        context = {
            'message': 'Aucune donnée trouvée pour les critères sélectionnés.',
            'niveaux': niveaux,
            'annees_scolaires': annees_scolaires,
            'niveau_id': niveau_ids,
            'annee_scolaire_id': annee_scolaire_id,
            'trimestre': trimestre,
        }
        return render(request, 'bulletins/bulletins_trimestriels_niveau.html', context)

    bulletins_trimestriels = {}
    for note in notes:
        eleve = note.eleve
        if eleve.id not in bulletins_trimestriels:
            bulletins_trimestriels[eleve.id] = {
                'eleve': eleve,
                'notes_par_matiere': [],
                'moyenne_totale': 0,
            }
        bulletins_trimestriels[eleve.id]['notes_par_matiere'].append({
            'matiere__nom': note.matiere.nom,
            'moyenne_matiere': note.moyenne,
        })
        bulletins_trimestriels[eleve.id]['moyenne_totale'] += note.moyenne

    for bulletin in bulletins_trimestriels.values():
        total_notes = len(bulletin['notes_par_matiere'])
        if total_notes > 0:
            bulletin['moyenne_totale'] = round(bulletin['moyenne_totale'] / total_notes, 2)

    bulletins_trimestriels_avec_moyenne = sorted(
        bulletins_trimestriels.values(),
        key=lambda b: b.get('moyenne_totale', 0),
        reverse=True
    )

    # Classement et observation
    last_rank = 1
    last_score = bulletins_trimestriels_avec_moyenne[0]['moyenne_totale']
    for idx, bulletin in enumerate(bulletins_trimestriels_avec_moyenne):
        if bulletin['moyenne_totale'] == last_score:
            bulletin['rang'] = last_rank
        else:
            last_rank = idx + 1
            bulletin['rang'] = last_rank
        last_score = bulletin['moyenne_totale']

        bulletin['rang_formate'] = format_rang(bulletin['rang'])

        if bulletin['moyenne_totale'] >= 10:
            bulletin['observation'] = "Excellent"
        elif bulletin['moyenne_totale'] >= 8:
            bulletin['observation'] = "Très Bien"
        elif bulletin['moyenne_totale'] >= 7:
            bulletin['observation'] = "Bien"
        elif bulletin['moyenne_totale'] >= 6:
            bulletin['observation'] = "Assez Bien"
        elif bulletin['moyenne_totale'] >= 5:
            bulletin['observation'] = "Passable"
        else:
            bulletin['observation'] = "Médiocre"

    # Récupération des objets
    niveau_obj = Niveau.objects.filter(id__in=niveau_ids).first() if niveau_ids else None
    annee_scolaire_obj = AnneeScolaire.objects.filter(id=annee_scolaire_id).first() if annee_scolaire_id else None

    context = {
        'bulletins_trimestriels': bulletins_trimestriels_avec_moyenne,
        'niveaux': niveaux,
        'annees_scolaires': annees_scolaires,
        'niveau_obj': niveau_obj,
        'annee_scolaire_obj': annee_scolaire_obj,
        'niveau_id': niveau_ids,
        'annee_scolaire_id': annee_scolaire_id,
        'trimestre': trimestre,
    }
    return render(request, 'bulletins/bulletins_trimestriels_niveau.html', context)

############################## FIN ######################################

# LES BULLETINS PAR CLASSE OU OPTION
def determiner_observation(moyenne):
    """Détermine l'observation en fonction de la moyenne de l'élève."""
    
    if moyenne >= 10:
        return "Très Bien"
    elif moyenne >= 8:
        return "Très Bien"

    elif moyenne >= 7:
        return "Bien"
    elif moyenne >= 6:
        return "Assez Bien"
    elif moyenne >= 5:
        return "Passable"
    else:
        return "Médiocre"

def formater_rang(rang):
    """Formate le rang avec un suffixe approprié."""
    if rang == 1:
        return f"{rang}er"  # "1er"
    elif rang == 2:
        return f"{rang}ème"  # "2ème"
    elif rang == 3:
        return f"{rang}ème"  # "3ème"
    else:
        return f"{rang}ème"  # Pour tous les autres rangs, on met "ème"

def bulletins_trimestriels_classe(request):
    annee_scolaire_id = request.GET.get("annee_scolaire")
    groupe_classe_id = request.GET.get("groupe_classe")
    trimestre = request.GET.get("trimestre")

    # Récupérer toutes les notes pour les élèves du groupe et de l'année scolaire
    notes = Note.objects.filter(
        eleve__groupe_classe_id=groupe_classe_id,
        annee_scolaire_id=annee_scolaire_id,
        trimestre=trimestre,
    ).select_related("matiere", "eleve", "annee_scolaire")

    bulletins = {}
    
    # Processus de collecte des notes par matière et calcul de la moyenne totale
    for note in notes:
        eleve = note.eleve
        if eleve.id not in bulletins:
            bulletins[eleve.id] = {
                "eleve": eleve,
                "notes_par_matiere": [],
                "moyenne_totale": 0,
            }
        moyenne_matiere = note.moyenne if note.moyenne is not None else 0  # Vérification
        bulletins[eleve.id]["notes_par_matiere"].append({
            "matiere__nom": note.matiere.nom,
            "moyenne_matiere": moyenne_matiere,
        })
        bulletins[eleve.id]["moyenne_totale"] += moyenne_matiere

    # Calcul de la moyenne générale de chaque élève
    for bulletin in bulletins.values():
        total_notes = len(bulletin["notes_par_matiere"])
        if total_notes > 0:
            bulletin["moyenne_totale"] = round(bulletin["moyenne_totale"] / total_notes, 2)
        else:
            bulletin["moyenne_totale"] = 0  # Évite les erreurs

    # Créer une liste à partir du dictionnaire et trier par moyenne
    bulletins_list = list(bulletins.values())
    bulletins_list.sort(key=lambda x: x["moyenne_totale"], reverse=True)

    # Gestion des ex æquo et attribution du rang
    current_rank = 1
    last_moyenne = None
    for i, bulletin in enumerate(bulletins_list):
        if bulletin["moyenne_totale"] != last_moyenne:
            current_rank = i + 1  # Le rang commence à partir de 1
        bulletin["rang"] = current_rank
        bulletin["rang_formate"] = formater_rang(current_rank)  # Appliquer le formatage du rang
        
        # Déterminer l'observation en fonction de la moyenne
        bulletin["observation"] = determiner_observation(bulletin["moyenne_totale"])

        last_moyenne = bulletin["moyenne_totale"]

    # Passer les bulletins aux templates
    context = {
        "bulletins_trimestriels": bulletins_list,
        "annees_scolaires": AnneeScolaire.objects.all(),
        "groupes_classes": GroupeClasse.objects.all(),
        "trimestre": trimestre,  # Ajouter la variable trimestre au contexte
    }
    return render(request, "bulletins/bulletins_trimestriels_classe.html", context)
############################################################################
#  RESUTALTS DES BULLETINS
def resultat_trimestriel_classe(request):
    groupe_classe_id = request.GET.get('groupe_classe')
    annee_scolaire_id = request.GET.get('annee_scolaire')
    trimestre = request.GET.get('trimestre')

    # Récupération des données pour les champs de sélection
    groupes_classes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    # Validation des paramètres requis
    if not groupe_classe_id or not annee_scolaire_id or not trimestre:
        return render(request, 'bulletins/resultat_trimestriel_classe.html', {
            'error_message': 'Veuillez sélectionner tous les filtres nécessaires.',
            'groupes_classes': groupes_classes,
            'annees_scolaires': annees_scolaires,
        })

    try:
        groupe_classe_obj = GroupeClasse.objects.get(id=groupe_classe_id)  # Récupère l'objet du groupe
        annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_scolaire_id)  # Récupère l'objet de l'année scolaire
        trimestre = int(trimestre)

        trimestre_label = f"{trimestre}ᵉ"
    except GroupeClasse.DoesNotExist or AnneeScolaire.DoesNotExist:
        return render(request, 'bulletins/resultat_trimestriel_classe.html', {
            'error_message': 'La classe ou l\'année scolaire n\'existe pas.',
            'groupes_classes': groupes_classes,
            'annees_scolaires': annees_scolaires,
        })

    # Récupération des bulletins du groupe classe, année scolaire et trimestre sélectionnés
    bulletins = BulletinTrimestriel.objects.filter(
        eleve__groupe_classe_id=groupe_classe_id,
        annee_scolaire_id=annee_scolaire_id,
        trimestre=trimestre
    )

    # Ajout des moyennes et observations
    bulletins_with_data = []
    for bulletin in bulletins:
        moyenne = bulletin.moyenne_totale or 0
        if moyenne >= 10:
            observation = "Excellent"
        elif moyenne >= 8:
            observation = "Très bien"
        elif moyenne >= 7:
            observation = "Bien"
        elif moyenne >= 6:
            observation = "Assez Bien"
        elif moyenne >= 5:
            observation = "Passable"
        else:
            observation = "Médiocre"
        
        bulletins_with_data.append({
            'bulletin': bulletin,
            'moyenne': moyenne,
            'observation': observation,
        })

    # Tri des bulletins par moyenne décroissante
    sorted_bulletins = sorted(
        bulletins_with_data,
        key=lambda b: b['moyenne'],
        reverse=True
    )

    # Calcul des rangs avec gestion des exæquo
    previous_moyenne = None
    current_rank = 0
    rank_count = 0  # Nombre d'ex æquo

    for index, data in enumerate(sorted_bulletins):
        # Si la moyenne est la même que celle du bulletin précédent, c'est un ex æquo
        if previous_moyenne is not None and data['moyenne'] == previous_moyenne:
            rank_count += 1  # Incrémenter le compteur des ex æquo
        else:
            current_rank += rank_count + 1  # On saute le nombre d'ex æquo
            rank_count = 0  # Réinitialiser le compteur des ex æquo

        # Si ex æquo, ajouter "Ex" au rang
        if rank_count > 0:
            data['rang'] = f"{current_rank}{get_ordinal_suffix(current_rank)} Ex"
        else:
            data['rang'] = f"{current_rank}{get_ordinal_suffix(current_rank)}"

        # Mettre à jour la moyenne précédente
        previous_moyenne = data['moyenne']

    return render(request, 'bulletins/resultat_trimestriel_classe.html', {
        'groupes_classes': groupes_classes,
        'annees_scolaires': annees_scolaires,
        'sorted_bulletins': sorted_bulletins,
        'groupe_obj': groupe_classe_obj,  # Ajouter l'objet du groupe
        'annee_scolaire_obj': annee_scolaire_obj,  # Ajouter l'objet de l'année scolaire
         'trimestre_label' : trimestre_label 

    })


# RESULTAT ANNUEL PAR GROUPE DE CLASSE OU OPTION EN FONCTION DE L'ANNEE SCOLAIRE
def resultat_annuel_classe(request):
    groupe_classe_id = request.GET.get('groupe_classe')
    annee_scolaire_id = request.GET.get('annee_scolaire')

    # Récupération des groupes de classes et des années scolaires pour le formulaire
    groupes_classes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    # Debug : Imprimer les valeurs des paramètres
    print(f"groupe_classe_id: {groupe_classe_id}, annee_scolaire_id: {annee_scolaire_id}")

    # Validation des paramètres requis
    if not groupe_classe_id or not annee_scolaire_id:
        return render(request, 'bulletins/resultat_annuel_classe.html', {
            'error_message': 'Veuillez sélectionner tous les filtres nécessaires.',
            'groupes_classes': groupes_classes,
            'annees_scolaires': annees_scolaires,
        })

    # Récupération des bulletins annuels pour le groupe de classe et l'année scolaire sélectionnés
    bulletins_annuels = BulletinAnnuel.objects.filter(
        eleve__groupe_classe_id=groupe_classe_id,
        annee_scolaire_id=annee_scolaire_id
    )

    # Debug : Vérifier si des bulletins sont récupérés
    print(f"Bulletins récupérés: {bulletins_annuels.count()}")

    # Si aucun bulletin n'est trouvé
    if bulletins_annuels.count() == 0:
        return render(request, 'bulletins/resultat_annuel_classe.html', {
            'error_message': 'Aucun bulletin trouvé pour les critères sélectionnés.',
            'groupes_classes': groupes_classes,
            'annees_scolaires': annees_scolaires,
        })

    # Ajout des moyennes annuelles et observations
    bulletins_with_data = []
    for bulletin in bulletins_annuels:
        # Utilisation des propriétés pour récupérer les moyennes par trimestre et la moyenne annuelle
        moyennes = bulletin.moyenne_totale_par_trimestre
        moyenne_annuelle = bulletin.moyenne_totale_annuelle

        # Définition de l'observation en fonction de la moyenne annuelle
        if moyenne_annuelle >= 10:
            observation = "Excellent"
        elif moyenne_annuelle >= 8:
            observation = "Très bien"
        elif moyenne_annuelle >= 7:
            observation = "Bien"
        elif moyenne_annuelle >= 6:
            observation = "Assez Bien"
        elif moyenne_annuelle >= 5:
            observation = "Passable"
        else:
            observation = "Médiocre"

        bulletins_with_data.append({
            'bulletin': bulletin,
            'moyenne_t1': moyennes['moyenne_t1'],
            'moyenne_t2': moyennes['moyenne_t2'],
            'moyenne_annuelle': moyenne_annuelle,
            'observation': observation,
        })

    # Tri des bulletins par moyenne annuelle (par ordre décroissant)
    sorted_bulletins = sorted(bulletins_with_data, key=lambda b: b['moyenne_annuelle'], reverse=True)

    # Calcul des rangs
    for index, data in enumerate(sorted_bulletins):
        data['rang'] = index + 1

    groupe_classe_obj = GroupeClasse.objects.get(id=groupe_classe_id)
    annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_scolaire_id)

    return render(request, 'bulletins/resultat_annuel_classe.html', {
        'groupes_classes': groupes_classes,
        'annees_scolaires': annees_scolaires,
        'sorted_bulletins': sorted_bulletins,
        'groupe_obj': groupe_classe_obj,  # Ajout de l'objet groupe_classe
        'annee_scolaire_obj': annee_scolaire_obj,  # Ajout de l'objet annee_scolaire
    })
################################ FIN #######################################################

########## AFICHARGE DES RESULTATS TRIMESTRIELS PAR NIVEAU ET ANNEE SCOLAIRE
def resultats_trimestriels_niveau(request):
    niveau_id = request.GET.get('niveau')
    annee_scolaire_id = request.GET.get('annee_scolaire')
    trimestre = request.GET.get('trimestre')

    niveaux = Niveau.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    if not niveau_id or not annee_scolaire_id or not trimestre:
        return render(request, 'bulletins/resultats_trimestriels_niveau.html', {
            'error_message': 'Veuillez sélectionner tous les filtres nécessaires.',
            'niveaux': niveaux,
            'annees_scolaires': annees_scolaires,
        })

    try:
        niveau_id = int(niveau_id)
        annee_scolaire_id = int(annee_scolaire_id)
        trimestre = int(trimestre)

        annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_scolaire_id)
        niveau_obj = Niveau.objects.get(id=niveau_id)
        trimestre_label = f"{trimestre}ᵉ"

        bulletins = BulletinTrimestriel.objects.filter(
            annee_scolaire_id=annee_scolaire_id,
            eleve__niveau_id=niveau_id,
            trimestre=trimestre
        ).select_related("eleve")

    except (ValueError, AnneeScolaire.DoesNotExist, Niveau.DoesNotExist):
        return render(request, 'bulletins/resultats_trimestriels_niveau.html', {
            'error_message': 'Paramètres de filtrage invalides.',
            'niveaux': niveaux,
            'annees_scolaires': annees_scolaires,
        })

    bulletins_list = []
    for bulletin in bulletins:
        moyenne = bulletin.moyenne_totale if bulletin.moyenne_totale is not None else 0

        if moyenne >= 10:
            observation = "Excellent"
        elif moyenne >= 8:
            observation = "Très bien"
        elif moyenne >= 7:
            observation = "Bien"
        elif moyenne >= 6:
            observation = "Assez Bien"
        elif moyenne >= 5:
            observation = "Passable"
        else:
            observation = "Médiocre"

        bulletin.moyenne = moyenne
        bulletin.observation = observation
        bulletin.rang = None  # temporaire
        bulletins_list.append(bulletin)

    sorted_bulletins = sorted(bulletins_list, key=lambda b: b.moyenne, reverse=True)

    # Gestion du rang avec égalité
    rank = 1
    previous_moyenne = None
    equal_rank = 0
    for i, bulletin in enumerate(sorted_bulletins):
        current_moyenne = bulletin.moyenne

        if previous_moyenne is None or current_moyenne != previous_moyenne:
            if equal_rank > 0:
                for j in range(equal_rank):
                    sorted_bulletins[i - 1 - j].rang = f"{rank}ème Ex"
            bulletin.rang = f"{rank}er" if rank == 1 else f"{rank}ème"
            previous_moyenne = current_moyenne
            equal_rank = 0
            rank += 1
        else:
            bulletin.rang = f"{rank - 1}ème"
            equal_rank += 1

    if equal_rank > 0:
        for j in range(equal_rank):
            sorted_bulletins[-1 - j].rang = f"{rank - 1}ème Ex"

    return render(request, 'bulletins/resultats_trimestriels_niveau.html', {
        'niveaux': niveaux,
        'annees_scolaires': annees_scolaires,
        'sorted_bulletins': sorted_bulletins,
        'trimestre_selectionne': trimestre,
        'trimestre_label': trimestre_label,
        'annee_scolaire_obj': annee_scolaire_obj,
        'niveau_obj': niveau_obj,
    })

################## AFFICHARGE DU RESULTAT ANNUEL PAS NIVEAU ET ANNEE SCOLAIRE ########
def get_ordinal_suffix(rank):
    """ Retourne le suffixe ordinal français (1er, 2ème, 3ème...) """
    if rank == 1:
        return "er"
    elif rank == 2:
        return "ème"
    elif rank == 3:
        return "ème"
    # Gérer les autres rangs, comme "4ème", "5ème", etc.
    return f"{rank}ème"

def get_observation(moyenne):
    """ Retourne l'observation en fonction de la moyenne de l'élève """
    if moyenne >= 10:
        return "Excellent"
    elif moyenne >= 8:
        return "Très bien"
    elif moyenne >= 7:
        return "Bien"
    elif moyenne >= 6:
        return "Assez Bien"
    elif moyenne >= 5:
        return "Passable"
    else:
        return "Médiocre"

def resultats_annuels_niveau(request):
    niveau_id = request.GET.get('niveau')
    annee_scolaire_id = request.GET.get('annee_scolaire')

    niveaux = Niveau.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()

    if not niveau_id or not annee_scolaire_id:
        return render(request, 'bulletins/resultats_annuels_niveau.html', {
            'error_message': 'Veuillez sélectionner tous les filtres nécessaires.',
            'niveaux': niveaux,
            'annees_scolaires': annees_scolaires,
        })

    try:
        niveau_id = int(niveau_id)
        annee_scolaire_id = int(annee_scolaire_id)
        niveau_obj = Niveau.objects.get(id=niveau_id)
        annee_scolaire_obj = AnneeScolaire.objects.get(id=annee_scolaire_id)

        # Récupérer les bulletins (sans tri)
        bulletins = list(BulletinAnnuel.objects.filter(
            annee_scolaire_id=annee_scolaire_id,
            eleve__niveau_id=niveau_id
        ))

        # Trier les bulletins par moyenne annuelle décroissante
        bulletins.sort(key=lambda b: b.moyenne_totale_annuelle, reverse=True)

        ranked_bulletins = []
        previous_moyenne = None
        current_rank = 0
        rank_count = 0  # Nombre d'ex æquo

        for index, bulletin in enumerate(bulletins, start=1):
            if previous_moyenne is not None and bulletin.moyenne_totale_annuelle == previous_moyenne:
                rank_count += 1  # Comptage des ex æquo
            else:
                current_rank += rank_count + 1  # Sauter les ex æquo
                rank_count = 0  # Réinitialisation

            # Si ex æquo, ne pas ajouter "Ex" au rang de manière systématique
            if rank_count > 0:
                rang = f"{current_rank}{get_ordinal_suffix(current_rank)} Ex"
            else:
                rang = f"{current_rank}{get_ordinal_suffix(current_rank)}"

            # Calcul de l'observation en fonction de la moyenne
            observation = get_observation(bulletin.moyenne_totale_annuelle)

            ranked_bulletins.append({
                'eleve': bulletin.eleve,  # On stocke l'objet eleve
                'moyenne_annuelle': bulletin.moyenne_totale_annuelle,
                'rang': rang,
                'observation': observation
            })

            previous_moyenne = bulletin.moyenne_totale_annuelle

    except ValueError:
        return render(request, 'bulletins/resultats_annuels_niveau.html', {
            'error_message': 'Paramètres de filtrage invalides.',
            'niveaux': niveaux,
            'annees_scolaires': annees_scolaires,
        })

    return render(request, 'bulletins/resultats_annuels_niveau.html', {
    'bulletins': ranked_bulletins,
    'niveaux': niveaux,
    'annees_scolaires': annees_scolaires,
    'niveau_selectionne': niveau_id,
    'annee_scolaire_selectionnee': annee_scolaire_id,
    'niveau_obj': niveau_obj,
    'annee_scolaire_obj': annee_scolaire_obj,
})
#########################################################################
#VALIDATION DES BULLETINS TRIMESTRIELL ET ANNUELS
#CREATION DES BULLETINS
def valider_bulletin_trimestre(request):
    if request.method == 'POST':
        annee_scolaire_id = request.POST.get('annee_scolaire')
        groupe_classe_id = request.POST.get('groupe_classe')
        trimestre = request.POST.get('trimestre', 1)  # Par défaut, trimestre 1 si non spécifié

        # Vérifiez que les champs sont remplis
        if not annee_scolaire_id or not groupe_classe_id:
            messages.error(request, "Veuillez sélectionner une année scolaire et un groupe de classe.")
            return redirect('valider-bulletin-trimestre')  # Remplacez par le nom de votre URL

        # Récupérer les données sélectionnées
        try:
            annee_scolaire = AnneeScolaire.objects.get(id=annee_scolaire_id)
            groupe_classe = GroupeClasse.objects.get(id=groupe_classe_id)
        except (AnneeScolaire.DoesNotExist, GroupeClasse.DoesNotExist):
            messages.error(request, "Les données sélectionnées sont invalides.")
            return redirect('trimestre')

        # Récupérer les élèves du groupe de classe
        eleves = Eleve.objects.filter(groupe_classe=groupe_classe, annee_scolaire=annee_scolaire)

        if not eleves.exists():
            messages.warning(request, "Aucun élève trouvé pour ce groupe de classe et cette année scolaire.")
            return redirect('trimestre')

        # Créer les bulletins trimestriels pour chaque élève
        for eleve in eleves:
            # Vérifier si le bulletin existe déjà
            bulletin_existe = BulletinTrimestriel.objects.filter(
                eleve=eleve,
                trimestre=trimestre,
                annee_scolaire=annee_scolaire
            ).exists()

            if not bulletin_existe:
                BulletinTrimestriel.objects.create(
                    eleve=eleve,
                    trimestre=trimestre,
                    annee_scolaire=annee_scolaire
                )

        messages.success(request, "Les bulletins ont été validés avec succès.")
        return redirect('trimestre')  # Redirigez vers la page pour afficher le succès

    # Charger les données pour le formulaire
    annees_scolaires = AnneeScolaire.objects.all()
    groupes_classes = GroupeClasse.objects.all()

    return render(request, 'bulletins/valider_bulletin_trimestre.html', {
        'annees_scolaires': annees_scolaires,
        'groupes_classes': groupes_classes,
    })


#VALIDATION DES BULLETINS ANNUELS
def valider_bulletin_annuel(request):
    if request.method == 'POST':
        annee_scolaire_id = request.POST.get('annee_scolaire')
        groupe_classe_id = request.POST.get('groupe_classe')

        # Vérifiez que les champs sont remplis
        if not annee_scolaire_id or not groupe_classe_id:
            messages.error(request, "Veuillez sélectionner une année scolaire et un groupe de classe.")
            return redirect('valider_bulletin')  # Remplacez par le nom de votre URL

        # Récupérer les données sélectionnées
        try:
            annee_scolaire = AnneeScolaire.objects.get(id=annee_scolaire_id)
            groupe_classe = GroupeClasse.objects.get(id=groupe_classe_id)
        except (AnneeScolaire.DoesNotExist, GroupeClasse.DoesNotExist):
            messages.error(request, "Les données sélectionnées sont invalides.")
            return redirect('valider_bulletin')

        # Récupérer les élèves du groupe de classe et de l'année scolaire
        eleves = Eleve.objects.filter(groupe_classe=groupe_classe, annee_scolaire=annee_scolaire)

        if not eleves.exists():
            messages.warning(request, "Aucun élève trouvé pour ce groupe de classe et cette année scolaire.")
            return redirect('valider_bulletin')

        # Créer ou valider les bulletins annuels pour chaque élève
        for eleve in eleves:
            # Vérifier si le bulletin annuel existe déjà pour l'élève et l'année scolaire
            bulletin_existe = BulletinAnnuel.objects.filter(
                eleve=eleve,
                annee_scolaire=annee_scolaire
            ).exists()

            if not bulletin_existe:
                BulletinAnnuel.objects.create(
                    eleve=eleve,
                    annee_scolaire=annee_scolaire
                )

        messages.success(request, "Les bulletins annuels ont été validés avec succès.")
        return redirect('valider_bulletin')  # Redirigez vers la page de validation

    # Charger les données pour le formulaire
    annees_scolaires = AnneeScolaire.objects.all()
    groupes_classes = GroupeClasse.objects.all()

    return render(request, 'bulletins/valider_bulletin_annuel.html', {
        'annees_scolaires': annees_scolaires,
        'groupes_classes': groupes_classes,
    })

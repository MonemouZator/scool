from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from matiere.models import Matiere
from eleve.models import Eleve,EleveInscrit
from annee_scolaire.models import AnneeScolaire
from note.models import Note
from groupe_classe.models import GroupeClasse
from django.contrib import messages
from niveau.models import Niveau
from django.utils.http import urlencode
from django.contrib.auth.decorators import login_required
from matiere.models import Matiere
from matiere.models import EnseignantMatiere



# Create your views here.

def note(request):
    matires=Matiere.objects.all()
    notes=Note.objects.all()
    annes=AnneeScolaire.objects.all()
    eleves=Eleve.objects.all()

    context={
                    "matires":matires,
                    "notes":notes,
                    "annes":annes,
                    "eleves":eleves
                }

    return render(request,'note/note.html',context)


#FONCTION DE MODIFICATION DES INFORMATIONS
def modifier(request):
    if request.method == 'POST':
        # Récupérer les données depuis la requête POST
        eleve = request.POST.get('eleve')
        matiere = request.POST.get('mat')
        anne = request.POST.get('anne')
        notecours = request.POST.get('nc')
        notecompo = request.POST.get('nco')
        trimestre = request.POST.get('trimestre')
        pk = request.POST.get('id')

        # Récupérer la note en fonction de l'ID
        note = get_object_or_404(Note, id=pk)

        # Assigner les nouveaux objets et valeurs à la note
        note.eleve = get_object_or_404(Eleve, id=eleve)
        note.matiere = get_object_or_404(Matiere, id=matiere)
        note.annee_scolaire = get_object_or_404(AnneeScolaire, id=anne)
        
        # Vérification si les notes sont valides (optionnel)
        try:
            note.note_cours = float(notecours)
            note.note_comp = float(notecompo)
        except ValueError:
            # Vous pouvez gérer une erreur si la conversion échoue (par exemple en renvoyant un message d'erreur)
            return redirect('note')  # Redirigez avec un message d'erreur approprié

        note.trimestre = trimestre

        # Sauvegarder la note modifiée
        note.save()

        # Rediriger après la sauvegarde
        return redirect('note')  # Rediriger vers la liste des notes
    else:
        return redirect('note')  # Rediriger vers la liste des notes en cas de méthode incorrecte
###############################################################
    #FONCTION DE SUPPRESSION DES INFORMATIONS
def  supprimer(request,pk):
    note=get_object_or_404(Note,id=pk)
    note.delete()

    return redirect('note')

###############################################################
# ATTRIBUTION DES NOTES AUX ELEVES



from django.http import JsonResponse


def attribuer_notes(request):
    niveaux = Niveau.objects.all()
    groupes = GroupeClasse.objects.all()
    annees_scolaires = AnneeScolaire.objects.all()
    matieres = Matiere.objects.all()

    niveau_id = request.GET.get('niveau')
    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')

    eleves = None
    try:
        if niveau_id and groupe_id and annee_id:
            niveau_id = int(niveau_id)
            groupe_id = int(groupe_id)
            annee_id = int(annee_id)
            eleves = Eleve.objects.filter(
                niveau_id=niveau_id,
                groupe_classe_id=groupe_id,
                annee_scolaire_id=annee_id
            )
    except (TypeError, ValueError):
        eleves = None

    if request.method == "POST":
        eleve_id = request.POST.get('eleve')
        annee_id_post = request.POST.get('anne')
        matiere_id = request.POST.get('mat')
        trimestre = request.POST.get('trimestre')
        note_cours = request.POST.get('nc')
        note_compo = request.POST.get('nco')

        if not (eleve_id and annee_id_post and matiere_id and trimestre and note_cours and note_compo):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Veuillez remplir tous les champs.'}, status=400)
            messages.error(request, "Veuillez remplir tous les champs.")
        else:
            eleve = get_object_or_404(Eleve, id=eleve_id)
            annee = get_object_or_404(AnneeScolaire, id=annee_id_post)
            matiere = get_object_or_404(Matiere, id=matiere_id)

            if Note.objects.filter(
                eleve=eleve,
                matiere=matiere,
                annee_scolaire=annee,
                trimestre=trimestre
            ).exists():
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': "Cet élève est déjà noté dans cette matière pour ce trimestre."}, status=400)
                messages.error(request, "Cet élève est déjà noté dans cette matière pour ce trimestre.")
            else:
                Note.objects.create(
                    eleve=eleve,
                    annee_scolaire=annee,
                    matiere=matiere,
                    trimestre=trimestre,
                    note_cours=note_cours,
                    note_comp=note_compo,
                )
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': 'Note ajoutée avec succès.'})
                messages.success(request, "Note ajoutée avec succès.")

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
    return render(request, 'note/rechercher_eleve.html', context)



###############################################################

#FONCTION DE MODIFICATION DES INFORMATIONS
def modifier(request):
    if request.method == 'POST':
        # Récupérer les données depuis la requête POST
        eleve = request.POST.get('eleve')
        matiere = request.POST.get('mat')
        anne = request.POST.get('anne')
        notecours = request.POST.get('nc')
        notecompo = request.POST.get('nco')
        trimestre = request.POST.get('trimestre')
        pk = request.POST.get('id')

        # Récupérer la note en fonction de l'ID
        note = get_object_or_404(Note, id=pk)

        # Assigner les nouveaux objets et valeurs à la note
        note.eleve = get_object_or_404(Eleve, id=eleve)
        note.matiere = get_object_or_404(Matiere, id=matiere)
        note.annee_scolaire = get_object_or_404(AnneeScolaire, id=anne)
        
        # Vérification si les notes sont valides (optionnel)
        try:
            note.note_cours = float(notecours)
            note.note_comp = float(notecompo)
        except ValueError:
            # Vous pouvez gérer une erreur si la conversion échoue (par exemple en renvoyant un message d'erreur)
            return redirect('note_enseignant')  # Redirigez avec un message d'erreur approprié

        note.trimestre = trimestre

        # Sauvegarder la note modifiée
        note.save()

        # Rediriger après la sauvegarde
        return redirect('note_enseignant')  # Rediriger vers la liste des notes
    else:
        return redirect('note_enseignant')  # Rediriger vers la liste des notes en cas de méthode incorrecte
###############################################################
    #FONCTION DE SUPPRESSION DES INFORMATIONS
def  supprimer(request,pk):
    note=get_object_or_404(Note,id=pk)
    note.delete()

    return redirect('note_enseignant')

# ATTRIBUTION DES NOTES AUX ELEVES PAR LES ENSEIGNANTS
def Liste_note_enseignant(request):
    matires=Matiere.objects.all()
    notes=Note.objects.all()
    annes=AnneeScolaire.objects.all()
    eleves=Eleve.objects.all()

    context={
                    "matires":matires,
                    "notes":notes,
                    "annes":annes,
                    "eleves":eleves
                }

    return render(request,'note/note_enseignant.html',context)


@login_required
def attribuer_note_enseignant(request):
    enseignant = getattr(request.user, 'enseignant_profile', None)
    if not enseignant:
        messages.error(request, "Vous n'êtes pas reconnu comme enseignant.")
        return render(request, 'note/rechercher_eleve2.html', {
            'niveaux': Niveau.objects.none(),
            'groupes': [],
            'annees_scolaires': AnneeScolaire.objects.all(),
        })

    # --- Niveaux autorisés pour cet enseignant ---
    niveaux_ids = EnseignantMatiere.objects.filter(
        enseignant=enseignant
    ).values_list('niveau_id', flat=True).distinct()
    niveaux = Niveau.objects.filter(id__in=niveaux_ids)

    groupes = []
    eleves = None
    matieres_autorisees = Matiere.objects.none()
    annees_scolaires = AnneeScolaire.objects.all()

    # --- FILTRES GET ---
    niveau_id = request.GET.get('niveau')
    groupe_id = request.GET.get('groupe_classe')
    annee_id = request.GET.get('annee_scolaire')

    if niveau_id:
        try:
            niveau_id = int(niveau_id)
            groupes = GroupeClasse.objects.filter(
                id__in=EnseignantMatiere.objects.filter(
                    enseignant=enseignant,
                    niveau_id=niveau_id
                ).values_list('groupe_classe_id', flat=True)
            ).order_by('nom')
        except:
            groupes = []

    if niveau_id and groupe_id and annee_id:
        try:
            groupe_id = int(groupe_id)
            annee_id = int(annee_id)
            eleves = Eleve.objects.filter(
                niveau_id=niveau_id,
                groupe_classe_id=groupe_id,
                annee_scolaire_id=annee_id
            )
            matieres_autorisees_ids = list(
                EnseignantMatiere.objects.filter(
                    enseignant=enseignant,
                    niveau_id=niveau_id,
                    groupe_classe_id=groupe_id
                ).values_list('matiere_id', flat=True)
            )
            matieres_autorisees = Matiere.objects.filter(id__in=matieres_autorisees_ids)
        except:
            eleves = None
            matieres_autorisees = Matiere.objects.none()

    # --- POST AJAX ---
    if request.method == "POST":
        eleve_id = request.POST.get('eleve')
        annee_id_post = request.POST.get('anne')
        matiere_id = request.POST.get('mat')
        trimestre = request.POST.get('trimestre')
        note_cours = request.POST.get('nc')
        note_compo = request.POST.get('nco')

        # Vérification des champs
        if not all([eleve_id, annee_id_post, matiere_id, trimestre, note_cours, note_compo]):
            return JsonResponse({'error': "Veuillez remplir tous les champs."}, status=400)

        try:
            eleve = Eleve.objects.get(id=eleve_id)
            annee = AnneeScolaire.objects.get(id=annee_id_post)
            matiere = Matiere.objects.get(id=matiere_id)
            trimestre = int(trimestre)
            note_cours = float(note_cours)
            note_compo = float(note_compo)
        except:
            return JsonResponse({'error': "Données invalides."}, status=400)

        # Vérifier si la matière est autorisée
        matieres_autorisees_post = Matiere.objects.filter(
            enseignantmatiere__enseignant=enseignant,
            enseignantmatiere__niveau=eleve.niveau,
            enseignantmatiere__groupe_classe=eleve.groupe_classe
        )

        if matiere not in matieres_autorisees_post:
            return JsonResponse({'error': "Vous n'êtes pas autorisé à noter cette matière."}, status=400)

        # Vérifier si la note existe déjà
        if Note.objects.filter(
            eleve=eleve,
            matiere=matiere,
            annee_scolaire=annee,
            trimestre=trimestre
        ).exists():
            return JsonResponse({'error': "Cet élève est déjà noté pour cette matière et ce trimestre."}, status=400)

        # --- LIAISON AVEC REINSCRIPTION ---
        inscription, created = EleveInscrit.objects.get_or_create(
            eleve=eleve,
            annee_scolaire=annee,
            defaults={
                'niveau': eleve.niveau,
                'groupe_classe': eleve.groupe_classe,
                'actif': True
            }
        )

        # Créer la note
        Note.objects.create(
            eleve=eleve,
            inscription=inscription,  # <-- Lien avec EleveInscrit
            annee_scolaire=annee,
            matiere=matiere,
            trimestre=trimestre,
            note_cours=note_cours,
            note_comp=note_compo
        )

        return JsonResponse({'success': "Note ajoutée avec succès."})

    # --- RENDER ---
    return render(request, 'note/rechercher_eleve2.html', {
        'niveaux': niveaux,
        'groupes': groupes,
        'annees_scolaires': annees_scolaires,
        'eleves': eleves,
        'matieres_autorisees': matieres_autorisees,
        'niveau_id': niveau_id,
        'groupe_id': groupe_id,
        'annee_id': annee_id,
    })




# Ajax groupes
@login_required
def ajax_groupes(request):
    niveau_id = request.GET.get('niveau')
    enseignant = getattr(request.user, 'enseignant_profile', None)
    groupes = []
    if niveau_id and enseignant:
        groupes_qs = GroupeClasse.objects.filter(
            id__in=EnseignantMatiere.objects.filter(
                enseignant=enseignant,
                niveau_id=niveau_id
            ).values_list('groupe_classe_id', flat=True)
        ).order_by('nom')
        groupes = [{'id': g.id, 'nom': g.nom} for g in groupes_qs]
    return JsonResponse(groupes, safe=False)

# Ajax matières
@login_required
def ajax_matieres(request):
    niveau_id = request.GET.get('niveau')
    groupe_id = request.GET.get('groupe')
    enseignant = getattr(request.user, 'enseignant_profile', None)
    matieres = []
    if niveau_id and groupe_id and enseignant:
        matieres_qs = EnseignantMatiere.objects.filter(
            enseignant=enseignant,
            niveau_id=niveau_id,
            groupe_classe_id=groupe_id
        ).select_related('matiere')

        matieres = [{
            'id': m.matiere.id,
            'nom': m.matiere.nom,
            'coefficient': m.matiere.coefficient,  # On garde juste le coefficient
        } for m in matieres_qs]

    return JsonResponse(matieres, safe=False)


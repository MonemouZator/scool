from django.shortcuts import render

# Create your views here.


# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from niveau.models import Niveau
from groupe_classe.models import GroupeClasse

# Create your views here.

def groupe(request):
    niveaus=Niveau.objects.all()
    groupes=GroupeClasse.objects.all()
    context={
                    "niveaus":niveaus,
                    "groupes":groupes
                }

    return render(request,'groupe/groupe.html',context)

# FONCTION D'ENREGISTREMENT DES ENSEIGNANTS


from django.contrib import messages
from django.db import IntegrityError


def ajout(request):
    if request.method == 'POST':
        niveau_id = request.POST.get('niveau')
        nom = request.POST.get('nom')

        # Vérifier si le groupe existe déjà pour ce niveau
        if GroupeClasse.objects.filter(nom=nom, niveau_id=niveau_id).exists():
            messages.error(request, f"Le groupe '{nom}' existe déjà pour ce niveau !")
            return redirect('groupe')

        try:
            groupe = GroupeClasse.objects.create(
                niveau=get_object_or_404(Niveau, id=niveau_id),
                nom=nom
            )
            groupe.save()
            messages.success(request, f"Groupe '{nom}' ajouté avec succès !")
        except IntegrityError:
            messages.error(request, "Erreur lors de l'ajout du groupe. Vérifiez les données.")
        
        return redirect('groupe')
    return redirect('groupe')


def modifier(request):
    if request.method == 'POST':
        pk = request.POST.get('id')
        niveau_id = request.POST.get('niveau')
        nom = request.POST.get('nom')

        groupe = get_object_or_404(GroupeClasse, id=pk)

        # Vérifier si le nom du groupe existe déjà pour ce niveau, autre que le groupe courant
        if GroupeClasse.objects.filter(nom=nom, niveau_id=niveau_id).exclude(id=pk).exists():
            messages.error(request, f"Le groupe '{nom}' existe déjà pour ce niveau !")
            return redirect('groupe')

        try:
            groupe.niveau = get_object_or_404(Niveau, id=niveau_id)
            groupe.nom = nom
            groupe.save()
            messages.success(request, f"Groupe '{nom}' modifié avec succès !")
        except IntegrityError:
            messages.error(request, "Erreur lors de la modification du groupe. Vérifiez les données.")

        return redirect('groupe')
    return redirect('groupe')


def supprimer(request, pk):
    groupe = get_object_or_404(GroupeClasse, id=pk)
    nom = groupe.nom
    try:
        groupe.delete()
        messages.success(request, f"Groupe '{nom}' supprimé avec succès !")
    except IntegrityError:
        messages.error(request, f"Impossible de supprimer le groupe '{nom}'. Il est utilisé ailleurs.")
    
    return redirect('groupe')



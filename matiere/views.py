from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from niveau.models import Niveau
from matiere.models import Matiere

# Create your views here.

def matiere(request):
    niveaus=Niveau.objects.all()
    matieres=Matiere.objects.all()
    context={
                    "niveaus":niveaus,
                    "matieres":matieres
                }

    return render(request,'matiere/matiere.html',context)

# FONCTION D'ENREGISTREMENT DES ENSEIGNANTS

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Matiere, Niveau

def ajout(request):
    if request.method == 'POST':
        niveau_id = request.POST.get('niveau')
        nom = request.POST.get('nom')
        coeff = request.POST.get('co')

        niveau = get_object_or_404(Niveau, id=niveau_id)

        # Vérifier si la matière existe déjà dans ce niveau
        if Matiere.objects.filter(nom=nom, niveau=niveau).exists():
            messages.error(request, f"La matière {nom} existe déjà pour la classe {niveau}.")
            return redirect('matiere')

        Matiere.objects.create(
            niveau=niveau,
            nom=nom,
            coefficient=coeff,
        )
        messages.success(request, f"Matière {nom} ajoutée avec succès à la classe {niveau}.")
        return redirect('matiere')

    return redirect('matiere')

    
    
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Matiere, Niveau

def modifier(request):
    if request.method == 'POST':
        niveau_id = request.POST.get('niveau')
        nom = request.POST.get('nom')
        coef = request.POST.get('co')
        pk = request.POST.get('id')

        matiere = get_object_or_404(Matiere, id=pk)
        niveau = get_object_or_404(Niveau, id=niveau_id)

        # Vérifier doublon (exclure la matière en cours de modif)
        if Matiere.objects.filter(niveau=niveau, nom__iexact=nom).exclude(id=pk).exists():
            messages.error(request, f"La matière {nom} existe déjà pour {niveau.nom}.")
            return redirect('matiere')

        matiere.niveau = niveau
        matiere.nom = nom
        matiere.coefficient = coef
        matiere.save()

        messages.success(request, f"Matière {nom} modifiée avec succès.")
        return redirect('matiere')
    return redirect('matiere')

    #FONCTION DE SUPPRESSION DES INFORMATIONS

def  supprimer(request,pk):
    matiere=get_object_or_404(Matiere,id=pk)
    matiere.delete()

    return redirect('matiere')

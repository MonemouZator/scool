from django.shortcuts import render

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from niveau.models import Niveau
from cycle.models import Cycle

# Create your views here.

def niveau(request):
    niveaus=Niveau.objects.all()
    cycles=Cycle.objects.all()
    context={
                    "niveaus":niveaus,
                    "cycles":cycles
                }

    return render(request,'niveau/niveau.html',context)

# FONCTION D'ENREGISTREMENT DES ENSEIGNANTS

from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import IntegrityError
from .models import Niveau
from cycle.models import Cycle

def ajout(request):
    if request.method == 'POST':
        cycle_id = request.POST.get('cy')
        nom = request.POST.get('nom')
        frais_scolaires = request.POST.get('frais_scolaires')

        # Vérifier si le niveau existe déjà
        if Niveau.objects.filter(nom=nom).exists():
            messages.error(request, f"Le niveau '{nom}' existe déjà !")
            return redirect('niveau')

        try:
            niveau = Niveau.objects.create(
                cycle=get_object_or_404(Cycle, id=cycle_id),
                nom=nom,
                montant_frais=Decimal(frais_scolaires.replace(',', '.'))
            )
            niveau.save()
            messages.success(request, f"Niveau '{nom}' ajouté avec succès !")
        except (ValueError, IntegrityError):
            messages.error(request, "Erreur lors de l'ajout du niveau. Vérifiez les données.")
        
        return redirect('niveau')
    return redirect('niveau')


def modifier(request):
    if request.method == 'POST':
        pk = request.POST.get('id')
        cycle_id = request.POST.get('cy')
        nom = request.POST.get('nom')
        frais_scolaires = request.POST.get('frais_scolaires')

        niveau = get_object_or_404(Niveau, id=pk)

        # Vérifier si le nom modifié existe déjà pour un autre niveau
        if Niveau.objects.filter(nom=nom).exclude(id=pk).exists():
            messages.error(request, f"Le niveau '{nom}' existe déjà !")
            return redirect('niveau')

        try:
            if cycle_id:
                niveau.cycle = get_object_or_404(Cycle, id=cycle_id)
            niveau.nom = nom
            niveau.montant_frais = Decimal(frais_scolaires.replace(',', '.'))
            niveau.save()
            messages.success(request, f"Niveau '{nom}' modifié avec succès !")
        except (ValueError, IntegrityError):
            messages.error(request, "Erreur lors de la modification du niveau. Vérifiez les données.")

        return redirect('niveau')
    return redirect('niveau')


def supprimer_niveau(request, pk):
    niveau = get_object_or_404(Niveau, pk=pk)
    nom = niveau.nom
    try:
        niveau.delete()
        messages.success(request, f"Niveau '{nom}' supprimé avec succès !")
    except IntegrityError:
        messages.error(request, f"Impossible de supprimer le niveau '{nom}'. Il est utilisé ailleurs.")
    return redirect('niveau')

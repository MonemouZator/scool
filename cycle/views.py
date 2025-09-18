from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from cycle.models import Cycle

# Create your views here.

def cycle(request):
    cycles=Cycle.objects.all()

    context={
                    "cycles":cycles
                }

    return render(request,'cycle/cycle.html',context)

# FONCTION D'ENREGISTREMENT DES ENSEIGNANTS

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cycle

# AJOUT
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # <-- ATTENTION ici
from .models import Cycle

def ajout(request):
    if request.method == "POST": 
        nom = request.POST.get('nom').strip()
        description = request.POST.get('des').strip()

        if Cycle.objects.filter(nom__iexact=nom).exists():
            messages.error(request, f"Le cycle '{nom}' existe déjà.")
            return redirect('cycle')

        Cycle.objects.create(nom=nom, description=description)
        messages.success(request, f"Cycle '{nom}' ajouté avec succès.")
        return redirect('cycle')
    return redirect('cycle')


def modifier(request):
    if request.method == 'POST':
        pk = request.POST.get('id')
        cycle = get_object_or_404(Cycle, id=pk)
        nom = request.POST.get('nom').strip()
        description = request.POST.get('des').strip()

        if Cycle.objects.filter(nom__iexact=nom).exclude(id=pk).exists():
            messages.error(request, f"Le cycle '{nom}' existe déjà.")
            return redirect('cycle')

        cycle.nom = nom
        cycle.description = description
        cycle.save()
        messages.success(request, f"Cycle '{nom}' modifié avec succès.")
        return redirect('cycle')
    return redirect('cycle')


def supprimer(request, pk):
    cycle = get_object_or_404(Cycle, id=pk)
    nom = cycle.nom
    cycle.delete()
    messages.success(request, f"Cycle '{nom}' supprimé avec succès.")
    return redirect('cycle')

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from cycle.models import Cycle,Etablissement

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



def profil_ecole(request):
    
    return render(request,'cycle/ajout_ecole.html')


def enregistrement(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        devise = request.POST.get('devise')
        pays = request.POST.get('pays')
        devise_pays = request.POST.get('devise_pays')
        logo = request.FILES.get('logo')
        date_creation = request.POST.get('date')
        meapu = request.POST.get('meapu')
        ire = request.POST.get('ire')
        dpe = request.POST.get('dpe')
        dsee = request.POST.get('dsee')
        respo = request.POST.get('respo')

        # Vérifier doublon par nom/prénom/niveau/année
        if Etablissement.objects.filter(
            nom_ecole=nom,
          
        ).exists():
            messages.error(request, "Cet établissement existe déjà.")
            return render(request, 'cycle/ajout_ecole.html')

        # Création de l'élève
        ecole = Etablissement.objects.create(
          
            nom_ecole=nom,
            devise_ecole=devise,
            date_creation=date_creation,
            pays=pays,
            devise_pays=devise_pays,
            meapu=meapu,
            ire=ire,
            dpe=dpe,
            dsee=dsee,
            logo=logo,
            responsable=respo,
        )
        ecole.save()

    else:
      return  redirect('afficharge_info_ecole')
    

def afficharge_info_ecole(request):
    etablissements=Etablissement.objects.all()

    context={
                    "etablissements":etablissements
                }

    return render(request,'cycle/afficharge_info_ecole.html',context)


def modifier(request, pk):
    ecolle = get_object_or_404(Etablissement, pk=pk)

    if request.method == 'POST':
        ecolle.nom_ecole = request.POST.get('nom')
        ecolle.devise_ecole = request.POST.get('devise')
        ecolle.date_creation = request.POST.get('date')
        ecolle.pays = request.POST.get('pays')
        ecolle.devise_pays = request.POST.get('devise_pays')
        ecolle.meapu = request.POST.get('meapu')
        ecolle.ire = request.POST.get('ire')
        ecolle.dpe = request.POST.get('dpe')
        ecolle.dsee = request.POST.get('dsee')
        ecolle.responsable = request.POST.get('respo')

        # ✅ Correction ici
        logo = request.FILES.get('logo')
        if logo:
            ecolle.logo = logo

        ecolle.save()
        messages.success(request, "Les informations de l'école ont été mises à jour avec succès.")
        return redirect('afficharge_info_ecole')

    return redirect('afficharge_info_ecole')

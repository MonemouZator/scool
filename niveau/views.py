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

def ajout(request):

    if request.method=='POST':
        cycle=request.POST.get('cy')
        nom=request.POST.get('nom')
        frais_scolaires=request.POST.get('frais_scolaires')
        niveau=Niveau.objects.create(

            cycle=get_object_or_404(Cycle,id=cycle),
            nom=nom,
            montant_frais=frais_scolaires,

          
        )
        niveau.save()

        return redirect('niveau')
    else:
        return redirect('niveau')
    

from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect

def modifier(request):
    if request.method == 'POST':
        # Récupérer les valeurs envoyées par le formulaire
        cycle = request.POST.get('cy')
        nom = request.POST.get('nom')
        pk = request.POST.get('id')  # Identifiant du niveau
        frais_scolaires = request.POST.get('frais_scolaires')

        # Obtenir l'objet 'niveau' en fonction de l'ID
        niveau = get_object_or_404(Niveau, id=pk)

        # Modifier les attributs du niveau
        if cycle:
            niveau.cycle = get_object_or_404(Cycle, id=cycle)  # Assurez-vous que le cycle existe
        niveau.nom = nom

        # Traitement de 'frais_scolaires' pour le convertir en Decimal
        try:
            frais_scolaires = frais_scolaires.replace(',', '.')  # Remplacer la virgule par un point
            niveau.montant_frais = Decimal(frais_scolaires)
        except ValueError:
            # Si la conversion échoue, vous pouvez retourner une erreur ou gérer autrement
            return redirect('niveau')  # ou afficher un message d'erreur à l'utilisateur

        # Sauvegarder les changements
        niveau.save()

        # Rediriger vers la page de gestion des niveaux (ou une autre page)
        return redirect('niveau')  # Remplacez 'niveau' par l'URL que vous souhaitez rediriger

    # Si ce n'est pas une méthode POST, rediriger vers une autre page ou afficher un message d'erreur
    return redirect('niveau')  # ou vous pouvez afficher un message d'erreur ici

    #FONCTION DE SUPPRESSION DES INFORMATIONS




     #FONCTION DE SUPPRESSION DES INFORMATIONS

def supprimer_niveau(request, pk):
    # Obtenez l'objet Niveau en fonction du pk
    niveau = get_object_or_404(Niveau, pk=pk)

    # Supprimez l'objet Niveau
    niveau.delete()

    # Redirigez vers la liste des niveaux après la suppression
    return redirect('niveau')  # Remplacez 'niveau' par le nom de l'URL à laquelle vous voulez rediriger

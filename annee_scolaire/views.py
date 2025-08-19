from django.shortcuts import render,redirect,get_object_or_404
from annee_scolaire.models import AnneeScolaire
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime

# Create your views here
def annee_scolaire(request):
    annees=AnneeScolaire.objects.all()

    context={
                    "annees":annees
                }

    return render(request,'annee/annee.html',context)

# FONCTION D'ENREGISTREMENT DES ANNEES SCOLAIRES

def ajout(request):

    if request.method == "POST":
        nom = request.POST.get('nom')
        debut = request.POST.get('debut')
        fin = request.POST.get('fin')

        # Vérifier doublon par annee
        if AnneeScolaire.objects.filter(nom=nom).exists():
            messages.error(request, "Cette année scolaire existe déjà veillez entrée une autre.")
            return redirect('an')


        # Convertir les dates en objets datetime.date
        try:
            date_debut = datetime.strptime(debut, "%Y-%m-%d").date()
            date_fin = datetime.strptime(fin, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Format de date invalide.")
            return redirect('an')

        # Vérifier que date_fin >= date_debut
        if date_fin < date_debut:
            messages.error(request, "La date de fin ne peut pas être antérieure à la date de début.")
            return redirect('an')

        # Créer l'année scolaire si tout est ok
        AnneeScolaire.objects.create(
            nom=nom,
            date_debut=date_debut,
            date_fin=date_fin
        )
        messages.error(request, "Date validée avec succès.")
        return redirect('an')
    else:
        return redirect('an')
    

def modifier(request):

    if request.method=='POST':
            pk=request.POST.get('id')
            ann=get_object_or_404(AnneeScolaire,id=pk)
            nom=request.POST.get('nom')
            debut=request.POST.get('debut')
            fin=request.POST.get('fin')

            ann.nom=nom
            ann.date_debut=debut
            ann.date_fin=fin
          
            ann.save()

            return redirect('an')
    else:
            return redirect('an')
    
    #FONCTION DE SUPPRESSION DES INFORMATIONS




     #FONCTION DE SUPPRESSION DES INFORMATIONS

def  supprimer(request,pk):
    annes=get_object_or_404(AnneeScolaire,id=pk)
    annes.delete()

    return redirect('an')

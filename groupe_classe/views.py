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

def ajout(request):

    if request.method=='POST':
        niveau=request.POST.get('niveau')
        nom=request.POST.get('nom')
        groupe=GroupeClasse.objects.create(

            niveau=get_object_or_404(Niveau,id=niveau),
            nom=nom,

          
        )
        groupe.save()

        return redirect('groupe')
    else:
        return redirect('groupe')
    
    
def modifier(request):

    if request.method=='POST':
            niveau=request.POST.get('niveau')
            nom=request.POST.get('nom')
            pk=request.POST.get('id')
            groupe=get_object_or_404(GroupeClasse,id=pk)
           
            groupe.niveau=get_object_or_404(Niveau,id=niveau)
            groupe.nom=nom
    
            groupe.save()

            return redirect('groupe')
    else:
            return redirect('groupe')
    
    #FONCTION DE SUPPRESSION DES INFORMATIONS




     #FONCTION DE SUPPRESSION DES INFORMATIONS

def  supprimer(request,pk):
    groupe=get_object_or_404(GroupeClasse,id=pk)
    groupe.delete()

    return redirect('groupe')

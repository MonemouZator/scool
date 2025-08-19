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

def ajout(request):

    if request.method=='POST':
        niveau=request.POST.get('niveau')
        nom=request.POST.get('nom')
        coeff=request.POST.get('co')
        mat=Matiere.objects.create(

            niveau=get_object_or_404(Niveau,id=niveau),
            nom=nom,
            coefficient=coeff,

          
        )
        mat.save()

        return redirect('matiere')
    else:
        return redirect('matiere')
    
    
def modifier(request):

    if request.method=='POST':
            niveau=request.POST.get('niveau')
            nom=request.POST.get('nom')
            coef=request.POST.get('co')
            pk=request.POST.get('id')
            matiere=get_object_or_404(Matiere,id=pk)
           
            matiere.niveau=get_object_or_404(Niveau,id=niveau)
            matiere.nom=nom
            matiere.coefficient=coef
    
            matiere.save()

            return redirect('matiere')
    else:
            return redirect('matiere')
    
    #FONCTION DE SUPPRESSION DES INFORMATIONS




     #FONCTION DE SUPPRESSION DES INFORMATIONS

def  supprimer(request,pk):
    matiere=get_object_or_404(Matiere,id=pk)
    matiere.delete()

    return redirect('matiere')

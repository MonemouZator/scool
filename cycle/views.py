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

def ajout(request):
    if request.method=="POST": 
           
            nom=request.POST.get('nom')
            desscription=request.POST.get('des')

           
            cycl=Cycle.objects.create(
                nom=nom,
                description=desscription,
               
            
            )
            cycl.save()

            return redirect('cycle')
    else:
        return redirect('cycle')
    
def modifier(request):

    if request.method=='POST':
            pk=request.POST.get('id')
            clase=get_object_or_404(Cycle,id=pk)
            nom=request.POST.get('nom')
            description=request.POST.get('des')
            

            clase.nom=nom
            clase.description=description
          
            clase.save()

            return redirect('cycle')
    else:
            return redirect('cycle')
    
    #FONCTION DE SUPPRESSION DES INFORMATIONS




     #FONCTION DE SUPPRESSION DES INFORMATIONS

def  supprimer(request,pk):
    cyc=get_object_or_404(Cycle,id=pk)
    cyc.delete()

    return redirect('cycle')

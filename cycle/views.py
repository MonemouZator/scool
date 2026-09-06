
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from cycle.models import Cycle, Etablissement


# ============================================================
# LISTE DES CYCLES
# ============================================================

def cycle(request):

    cycles = Cycle.objects.all()

    context = {
        "cycles": cycles
    }

    return render(request, 'cycle/cycle.html', context)


# ============================================================
# AJOUT D'UN CYCLE
# ============================================================

def ajout(request):

    if request.method == "POST":

        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('des', '').strip()

        # Vérification du nom
        if not nom:
            messages.error(
                request,
                "Veuillez renseigner le nom du cycle."
            )
            return redirect('cycle')

        # Vérification doublon
        if Cycle.objects.filter(nom__iexact=nom).exists():

            messages.error(
                request,
                f"Le cycle '{nom}' existe déjà."
            )

            return redirect('cycle')

        # Création
        Cycle.objects.create(
            nom=nom,
            description=description
        )

        messages.success(
            request,
            f"Cycle '{nom}' ajouté avec succès."
        )

        return redirect('cycle')

    return redirect('cycle')


# ============================================================
# MODIFICATION D'UN CYCLE
# ============================================================

def modifier(request):

    if request.method == 'POST':

        pk = request.POST.get('id')

        cycle_obj = get_object_or_404(
            Cycle,
            id=pk
        )

        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('des', '').strip()

        # Vérification du nom
        if not nom:

            messages.error(
                request,
                "Veuillez renseigner le nom du cycle."
            )

            return redirect('cycle')

        # Vérification doublon
        if Cycle.objects.filter(
            nom__iexact=nom
        ).exclude(
            id=pk
        ).exists():

            messages.error(
                request,
                f"Le cycle '{nom}' existe déjà."
            )

            return redirect('cycle')

        # Mise à jour
        cycle_obj.nom = nom
        cycle_obj.description = description
        cycle_obj.save()

        messages.success(
            request,
            f"Cycle '{nom}' modifié avec succès."
        )

        return redirect('cycle')

    return redirect('cycle')


# ============================================================
# SUPPRESSION D'UN CYCLE
# ============================================================

def supprimer(request, pk):

    cycle_obj = get_object_or_404(
        Cycle,
        id=pk
    )

    nom = cycle_obj.nom

    cycle_obj.delete()

    messages.success(
        request,
        f"Cycle '{nom}' supprimé avec succès."
    )

    return redirect('cycle')


# ============================================================
# FORMULAIRE INFORMATIONS ÉCOLE
# ============================================================

def profil_ecole(request):

    return render(
        request,
        'cycle/ajout_ecole.html'
    )


# ============================================================
# ENREGISTREMENT DES INFORMATIONS DE L'ÉCOLE
# ============================================================

def enregistrement(request):

    if request.method == 'POST':

        # ----------------------------------------------------
        # Récupération des données
        # ----------------------------------------------------

        nom = request.POST.get('nom', '').strip()
        devise = request.POST.get('devise', '').strip()
        pays = request.POST.get('pays', '').strip()
        devise_pays = request.POST.get('devise_pays', '').strip()

        date_creation = request.POST.get('date', '').strip()

        meapu = request.POST.get('meapu', '').strip()
        ire = request.POST.get('ire', '').strip()
        dpe = request.POST.get('dpe', '').strip()
        dsee = request.POST.get('dsee', '').strip()

        respo = request.POST.get('respo', '').strip()

        logo = request.FILES.get('logo')


        # ----------------------------------------------------
        # Vérification du nom de l'établissement
        # ----------------------------------------------------

        if not nom:

            messages.error(
                request,
                "Veuillez renseigner le nom de l'établissement."
            )

            return render(
                request,
                'cycle/ajout_ecole.html'
            )


        # ----------------------------------------------------
        # Vérification doublon
        # ----------------------------------------------------

        if Etablissement.objects.filter(
            nom_ecole__iexact=nom
        ).exists():

            messages.error(
                request,
                "Cet établissement existe déjà."
            )

            return render(
                request,
                'cycle/ajout_ecole.html'
            )


        # ----------------------------------------------------
        # Création de l'établissement
        # ----------------------------------------------------

        Etablissement.objects.create(

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


        # ----------------------------------------------------
        # Message de succès
        # ----------------------------------------------------

        messages.success(
            request,
            "Les informations de l'établissement ont été enregistrées avec succès."
        )


        # ----------------------------------------------------
        # IMPORTANT :
        # redirection après POST
        # ----------------------------------------------------

        return redirect(
            'afficharge_info_ecole'
        )


    # --------------------------------------------------------
    # Si la requête n'est pas POST
    # --------------------------------------------------------

    return redirect(
        'afficharge_info_ecole'
    )


# ============================================================
# AFFICHAGE DES INFORMATIONS DE L'ÉCOLE
# ============================================================

def afficharge_info_ecole(request):

    etablissements = Etablissement.objects.all()

    context = {
        "etablissements": etablissements
    }

    return render(
        request,
        'cycle/afficharge_info_ecole.html',
        context
    )


# ============================================================
# MODIFICATION DES INFORMATIONS DE L'ÉCOLE
# ============================================================

def modifier_info_ecole(request, pk):

    ecole = get_object_or_404(
        Etablissement,
        pk=pk
    )


    if request.method == 'POST':

        # ----------------------------------------------------
        # Récupération des données
        # ----------------------------------------------------

        ecole.nom_ecole = request.POST.get(
            'nom',
            ''
        ).strip()

        ecole.devise_ecole = request.POST.get(
            'devise',
            ''
        ).strip()

        ecole.date_creation = request.POST.get(
            'date',
            ''
        ).strip()

        ecole.pays = request.POST.get(
            'pays',
            ''
        ).strip()

        ecole.devise_pays = request.POST.get(
            'devise_pays',
            ''
        ).strip()

        ecole.meapu = request.POST.get(
            'meapu',
            ''
        ).strip()

        ecole.ire = request.POST.get(
            'ire',
            ''
        ).strip()

        ecole.dpe = request.POST.get(
            'dpe',
            ''
        ).strip()

        ecole.dsee = request.POST.get(
            'dsee',
            ''
        ).strip()

        ecole.responsable = request.POST.get(
            'respo',
            ''
        ).strip()


        # ----------------------------------------------------
        # Logo
        # ----------------------------------------------------

        logo = request.FILES.get('logo')

        if logo:
            ecole.logo = logo


        # ----------------------------------------------------
        # Sauvegarde
        # ----------------------------------------------------

        ecole.save()


        messages.success(
            request,
            "Les informations de l'école ont été mises à jour avec succès."
        )


        return redirect(
            'afficharge_info_ecole'
        )


    return redirect(
        'afficharge_info_ecole'
    )


# ============================================================
# SUPPRESSION DES INFORMATIONS DE L'ÉCOLE
# ============================================================

def supprimer_ecole(request, pk):

    if request.method == "POST":

        ecole = get_object_or_404(
            Etablissement,
            pk=pk
        )

        nom = ecole.nom_ecole

        ecole.delete()

        messages.success(
            request,
            f"L'établissement « {nom} » a été supprimé avec succès."
        )

    return redirect(
        'afficharge_info_ecole'
    )

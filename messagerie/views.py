from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Groupe,
    MembreGroupe,
    Message,
    MessageGroupe,
)


User = get_user_model()


# =========================================================
# MESSAGERIE PRINCIPALE
# =========================================================

@login_required
def boite_reception(request, utilisateur_id=None, groupe_id=None):

    utilisateur_selectionne = None
    groupe_selectionne = None

    conversation = Message.objects.none()
    conversation_groupe = MessageGroupe.objects.none()

    # =====================================================
    # TRAITEMENT DES FORMULAIRES
    # =====================================================

    if request.method == 'POST':

        type_message = request.POST.get(
            'type_message',
            ''
        )

        contenu = request.POST.get(
            'contenu',
            ''
        ).strip()

        # =================================================
        # MESSAGE INDIVIDUEL
        # =================================================

        if type_message == 'individuel':

            destinataire_id = request.POST.get(
                'destinataire'
            )

            if not destinataire_id or not contenu:

                messages.error(
                    request,
                    "Veuillez saisir un message."
                )

                if utilisateur_id:

                    return redirect(
                        'conversation',
                        utilisateur_id=utilisateur_id
                    )

                return redirect(
                    'boite_reception'
                )

            destinataire = get_object_or_404(
                User,
                pk=destinataire_id
            )

            # Empêcher l'auto-envoi
            if destinataire.pk == request.user.pk:

                messages.error(
                    request,
                    "Vous ne pouvez pas vous envoyer un message à vous-même."
                )

                return redirect(
                    'conversation',
                    utilisateur_id=destinataire.pk
                )

            # Création
            Message.objects.create(
                expediteur=request.user,
                destinataire=destinataire,
                objet="Message",
                contenu=contenu
            )

            # Ouvrir immédiatement la conversation
            return redirect(
                'conversation',
                utilisateur_id=destinataire.pk
            )

        # =================================================
        # MESSAGE GROUPE
        # =================================================

        elif type_message == 'groupe':

            groupe_id_post = request.POST.get(
                'groupe_id'
            )

            if not groupe_id_post or not contenu:

                messages.error(
                    request,
                    "Veuillez saisir un message."
                )

                if groupe_id:

                    return redirect(
                        'groupe_conversation',
                        groupe_id=groupe_id
                    )

                return redirect(
                    'boite_reception'
                )

            groupe = get_object_or_404(
                Groupe,
                pk=groupe_id_post,
                actif=True
            )

            # Vérifier l'appartenance au groupe
            membre = MembreGroupe.objects.filter(
                groupe=groupe,
                utilisateur=request.user,
                actif=True
            ).first()

            if not membre:

                messages.error(
                    request,
                    "Vous ne faites pas partie de ce groupe."
                )

                return redirect(
                    'boite_reception'
                )

            # Créer le message
            MessageGroupe.objects.create(
                groupe=groupe,
                expediteur=request.user,
                contenu=contenu
            )

            # Revenir au groupe
            return redirect(
                'groupe_conversation',
                groupe_id=groupe.pk
            )

    # =====================================================
    # CONVERSATIONS INDIVIDUELLES DISPONIBLES
    # =====================================================

    messages_utilisateur = (
        Message.objects
        .filter(
            Q(expediteur=request.user)
            |
            Q(destinataire=request.user)
        )
        .select_related(
            'expediteur',
            'destinataire'
        )
        .order_by('-date_envoi')
    )

    utilisateurs_ids = set()

    for msg in messages_utilisateur:

        if msg.expediteur_id != request.user.id:

            utilisateurs_ids.add(
                msg.expediteur_id
            )

        if msg.destinataire_id != request.user.id:

            utilisateurs_ids.add(
                msg.destinataire_id
            )

    utilisateurs_conversations = (
        User.objects
        .filter(
            pk__in=utilisateurs_ids
        )
        .exclude(
            pk=request.user.pk
        )
        .order_by('username')
    )

    # =====================================================
    # GROUPES DE L'UTILISATEUR
    # =====================================================

    groupes = (
        Groupe.objects
        .filter(
            membres__utilisateur=request.user,
            membres__actif=True,
            actif=True
        )
        .distinct()
        .order_by('nom')
    )

    # =====================================================
    # TOUS LES UTILISATEURS
    # =====================================================

    utilisateurs = (
        User.objects
        .exclude(
            pk=request.user.pk
        )
        .order_by('username')
    )

    # =====================================================
    # CONVERSATION INDIVIDUELLE SÉLECTIONNÉE
    # =====================================================

    if utilisateur_id:

        utilisateur_selectionne = get_object_or_404(
            User,
            pk=utilisateur_id
        )

        conversation = (
            Message.objects
            .filter(
                Q(
                    expediteur=request.user,
                    destinataire=utilisateur_selectionne
                )
                |
                Q(
                    expediteur=utilisateur_selectionne,
                    destinataire=request.user
                )
            )
            .select_related(
                'expediteur',
                'destinataire'
            )
            .order_by('date_envoi')
        )

        # Marquer comme lus
        Message.objects.filter(
            expediteur=utilisateur_selectionne,
            destinataire=request.user,
            lu=False
        ).update(
            lu=True
        )

    # =====================================================
    # GROUPE SÉLECTIONNÉ
    # =====================================================

    elif groupe_id:

        groupe_selectionne = get_object_or_404(
            Groupe,
            pk=groupe_id,
            actif=True
        )

        # Vérifier le membre
        membre = MembreGroupe.objects.filter(
            groupe=groupe_selectionne,
            utilisateur=request.user,
            actif=True
        ).first()

        if not membre:

            messages.error(
                request,
                "Vous n'avez pas accès à ce groupe."
            )

            return redirect(
                'boite_reception'
            )

        conversation_groupe = (
            MessageGroupe.objects
            .filter(
                groupe=groupe_selectionne
            )
            .select_related(
                'expediteur',
                'groupe'
            )
            .order_by('date_envoi')
        )

    # =====================================================
    # AUCUNE CONVERSATION SÉLECTIONNÉE
    #
    # OUVRIR AUTOMATIQUEMENT LA DERNIÈRE ACTIVITÉ
    # =====================================================

    else:

        derniere_activite = (
            Message.objects
            .filter(
                Q(expediteur=request.user)
                |
                Q(destinataire=request.user)
            )
            .select_related(
                'expediteur',
                'destinataire'
            )
            .order_by('-date_envoi')
            .first()
        )

        if derniere_activite:

            if derniere_activite.expediteur_id == request.user.id:

                autre_utilisateur_id = (
                    derniere_activite.destinataire_id
                )

            else:

                autre_utilisateur_id = (
                    derniere_activite.expediteur_id
                )

            return redirect(
                'conversation',
                utilisateur_id=autre_utilisateur_id
            )

        # S'il n'existe aucune conversation privée,
        # ouvrir le premier groupe disponible.
        premier_groupe = groupes.first()

        if premier_groupe:

            return redirect(
                'groupe_conversation',
                groupe_id=premier_groupe.pk
            )

    # =====================================================
    # MESSAGES NON LUS
    # =====================================================

    messages_non_lus = (
        Message.objects
        .filter(
            destinataire=request.user,
            lu=False
        )
        .count()
    )

    # =====================================================
    # CONTEXTE
    # =====================================================

    context = {

        'utilisateur_selectionne':
            utilisateur_selectionne,

        'groupe_selectionne':
            groupe_selectionne,

        'conversation':
            conversation,

        'conversation_groupe':
            conversation_groupe,

        'utilisateurs_conversations':
            utilisateurs_conversations,

        'groupes':
            groupes,

        'utilisateurs':
            utilisateurs,

        'messages_non_lus':
            messages_non_lus,
    }

    return render(
        request,
        'messagerie/boite_reception.html',
        context
    )


# =========================================================
# MESSAGES ENVOYÉS
# =========================================================

@login_required
def messages_envoyes(request):

    messages_env = (
        Message.objects
        .filter(
            expediteur=request.user
        )
        .select_related(
            'expediteur',
            'destinataire'
        )
        .order_by('-date_envoi')
    )

    return render(
        request,
        'messagerie/messages_envoyes.html',
        {
            'messages_env': messages_env
        }
    )


# =========================================================
# NOUVELLE CONVERSATION
# =========================================================

@login_required
def nouveau_message(request):

    # =====================================================
    # POST
    # =====================================================

    if request.method == 'POST':

        destinataire_id = request.POST.get(
            'destinataire'
        )

        contenu = request.POST.get(
            'contenu',
            ''
        ).strip()

        if not destinataire_id or not contenu:

            messages.error(
                request,
                "Veuillez remplir tous les champs."
            )

            return redirect(
                'nouveau_message'
            )

        destinataire = get_object_or_404(
            User,
            pk=destinataire_id
        )

        if destinataire.pk == request.user.pk:

            messages.error(
                request,
                "Vous ne pouvez pas vous envoyer un message à vous-même."
            )

            return redirect(
                'nouveau_message'
            )

        Message.objects.create(
            expediteur=request.user,
            destinataire=destinataire,
            objet="Message",
            contenu=contenu
        )

        return redirect(
            'conversation',
            utilisateur_id=destinataire.pk
        )

    # =====================================================
    # GET
    # =====================================================

    utilisateurs = (
        User.objects
        .exclude(
            pk=request.user.pk
        )
        .order_by('username')
    )

    return render(
        request,
        'messagerie/nouveau_message.html',
        {
            'utilisateurs':
                utilisateurs
        }
    )


# =========================================================
# LIRE UN MESSAGE INDIVIDUEL
# =========================================================

@login_required
def lire_message(request, pk):

    message = get_object_or_404(
        Message,
        pk=pk,
        destinataire=request.user
    )

    if not message.lu:

        message.lu = True

        message.save(
            update_fields=['lu']
        )

    return render(
        request,
        'messagerie/lire_message.html',
        {
            'message':
                message
        }
    )


# =========================================================
# SUPPRIMER UN MESSAGE
# =========================================================

@login_required
def supprimer_message(request, pk):

    message = get_object_or_404(
        Message,
        pk=pk,
        destinataire=request.user
    )

    if request.method == 'POST':

        message.delete()

        messages.success(
            request,
            "Message supprimé avec succès."
        )

    return redirect(
        'boite_reception'
    )


# =========================================================
# CRÉER UN GROUPE
# =========================================================

@login_required
def creer_groupe(request):

    if request.method == 'POST':

        nom = request.POST.get(
            'nom',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        membres_ids = request.POST.getlist(
            'membres'
        )

        if not nom:

            messages.error(
                request,
                "Le nom du groupe est obligatoire."
            )

            return redirect(
                'creer_groupe'
            )

        # Créer le groupe
        groupe = Groupe.objects.create(
            nom=nom,
            description=description,
            createur=request.user
        )

        # Ajouter automatiquement le créateur
        MembreGroupe.objects.create(
            groupe=groupe,
            utilisateur=request.user,
            administrateur=True
        )

        # Ajouter les membres sélectionnés
        for membre_id in membres_ids:

            if str(membre_id) == str(
                request.user.pk
            ):
                continue

            utilisateur = (
                User.objects
                .filter(pk=membre_id)
                .first()
            )

            if utilisateur:

                MembreGroupe.objects.get_or_create(
                    groupe=groupe,
                    utilisateur=utilisateur
                )

        messages.success(
            request,
            f"Le groupe « {groupe.nom} » a été créé avec succès."
        )

        return redirect(
            'groupe_conversation',
            groupe_id=groupe.pk
        )

    # =====================================================
    # GET
    # =====================================================

    utilisateurs = (
        User.objects
        .exclude(
            pk=request.user.pk
        )
        .order_by('username')
    )

    return render(
        request,
        'messagerie/groupe_creer.html',
        {
            'utilisateurs':
                utilisateurs
        }
    )

@login_required
def groupe_conversation(request, groupe_id):

    # =====================================================
    # RÉCUPÉRER LE GROUPE
    # =====================================================

    groupe = get_object_or_404(
        Groupe,
        pk=groupe_id,
        actif=True
    )


    # =====================================================
    # VÉRIFIER L'APPARTENANCE
    # =====================================================

    membre = MembreGroupe.objects.filter(
        groupe=groupe,
        utilisateur=request.user,
        actif=True
    ).first()


    if not membre:

        messages.error(
            request,
            "Vous ne faites pas partie de ce groupe."
        )

        return redirect('boite_reception')


    # =====================================================
    # ENVOI MESSAGE GROUPE
    # =====================================================

    if request.method == 'POST':

        type_message = request.POST.get(
            'type_message',
            ''
        )

        contenu = request.POST.get(
            'contenu',
            ''
        ).strip()

        groupe_id_post = request.POST.get(
            'groupe_id'
        )


        if type_message == 'groupe':

            if not contenu:

                messages.error(
                    request,
                    "Le message ne peut pas être vide."
                )

                return redirect(
                    'groupe_conversation',
                    groupe_id=groupe.id
                )


            if str(groupe_id_post) != str(groupe.id):

                messages.error(
                    request,
                    "Groupe invalide."
                )

                return redirect(
                    'groupe_conversation',
                    groupe_id=groupe.id
                )


            # -------------------------------------------------
            # CRÉER LE MESSAGE
            # -------------------------------------------------

            nouveau_message = MessageGroupe.objects.create(
                groupe=groupe,
                expediteur=request.user,
                contenu=contenu
            )


            # -------------------------------------------------
            # CONSIDÉRER LE MESSAGE COMME LU PAR L'EXPÉDITEUR
            # -------------------------------------------------

            request.session[
                f'messagerie_groupe_lu_{groupe.id}'
            ] = nouveau_message.id

            request.session.modified = True


            return redirect(
                'groupe_conversation',
                groupe_id=groupe.id
            )


    # =====================================================
    # RÉCUPÉRER LES MESSAGES
    # =====================================================

    conversation_groupe = (
        MessageGroupe.objects
        .filter(
            groupe=groupe
        )
        .select_related(
            'expediteur',
            'groupe'
        )
        .order_by('date_envoi')
    )


    # =====================================================
    # MARQUER LE GROUPE COMME LU
    # =====================================================

    dernier_message = (
        conversation_groupe
        .order_by('-id')
        .first()
    )


    if dernier_message:

        request.session[
            f'messagerie_groupe_lu_{groupe.id}'
        ] = dernier_message.id

        request.session.modified = True


    # =====================================================
    # GROUPES
    # =====================================================

    groupes = (
        Groupe.objects
        .filter(
            membres__utilisateur=request.user,
            membres__actif=True,
            actif=True
        )
        .distinct()
        .order_by('nom')
    )


    # =====================================================
    # AJOUTER LE NOMBRE DE NON-LUS À CHAQUE GROUPE
    # =====================================================

    for g in groupes:

        session_key = (
            f'messagerie_groupe_lu_{g.id}'
        )

        dernier_lu_id = request.session.get(
            session_key,
            0
        )

        g.messages_non_lus = (
            MessageGroupe.objects
            .filter(
                groupe=g,
                id__gt=dernier_lu_id
            )
            .exclude(
                expediteur=request.user
            )
            .count()
        )


    # =====================================================
    # CONVERSATIONS PRIVÉES
    # =====================================================

    messages_utilisateur = (
        Message.objects
        .filter(
            Q(expediteur=request.user) |
            Q(destinataire=request.user)
        )
        .select_related(
            'expediteur',
            'destinataire'
        )
    )


    utilisateurs_ids = set()


    for msg in messages_utilisateur:

        if msg.expediteur_id != request.user.id:

            utilisateurs_ids.add(
                msg.expediteur_id
            )

        if msg.destinataire_id != request.user.id:

            utilisateurs_ids.add(
                msg.destinataire_id
            )


    utilisateurs_conversations = (
        User.objects
        .filter(
            pk__in=utilisateurs_ids
        )
        .exclude(
            pk=request.user.pk
        )
        .order_by('username')
    )


    # =====================================================
    # NOMBRE DE MESSAGES NON LUS PAR UTILISATEUR
    # =====================================================

    for utilisateur in utilisateurs_conversations:

        utilisateur.messages_non_lus = (
            Message.objects
            .filter(
                expediteur=utilisateur,
                destinataire=request.user,
                lu=False
            )
            .count()
        )


    # =====================================================
    # TOUS LES UTILISATEURS
    # =====================================================

    utilisateurs = (
        User.objects
        .exclude(
            pk=request.user.pk
        )
        .order_by('username')
    )


    # =====================================================
    # TOTAL NON LUS PRIVÉS
    # =====================================================

    messages_prives_non_lus = (
        Message.objects
        .filter(
            destinataire=request.user,
            lu=False
        )
        .count()
    )


    # =====================================================
    # NON-LUS GROUPES
    # =====================================================

    messages_groupes_non_lus = 0


    for g in groupes:

        messages_groupes_non_lus += (
            getattr(
                g,
                'messages_non_lus',
                0
            )
        )


    # =====================================================
    # TOTAL
    # =====================================================

    messages_non_lus = (
        messages_prives_non_lus
        +
        messages_groupes_non_lus
    )


    # =====================================================
    # CONTEXTE
    # =====================================================

    context = {

        'utilisateur_selectionne':
            None,

        'groupe_selectionne':
            groupe,

        'conversation':
            Message.objects.none(),

        'conversation_groupe':
            conversation_groupe,

        'utilisateurs_conversations':
            utilisateurs_conversations,

        'groupes':
            groupes,

        'utilisateurs':
            utilisateurs,

        'messages_non_lus':
            messages_non_lus,

        'messages_prives_non_lus':
            messages_prives_non_lus,

        'messages_groupes_non_lus':
            messages_groupes_non_lus,
    }


    return render(
        request,
        'messagerie/boite_reception.html',
        context
    )
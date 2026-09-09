from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Groupe,
    MembreGroupe,
    Message,
    MessageGroupe,
    Notification,
)

User = get_user_model()


# =========================================================
# OUTILS
# =========================================================

def est_ajax(request):
    """
    Vérifie si la requête vient d'un appel AJAX.
    """
    return request.headers.get(
        "x-requested-with"
    ) == "XMLHttpRequest"


def nom_complet_utilisateur(user):
    """
    Retourne le nom complet de l'utilisateur.
    Compatible avec le modèle utilisateur actuel.
    """

    nom = getattr(user, "nom", "") or ""
    prenom = getattr(user, "prenom", "") or ""

    nom_complet = f"{nom} {prenom}".strip()

    if nom_complet:
        return nom_complet

    return getattr(
        user,
        "username",
        "Utilisateur"
    )


def texte_notification_prive(
    expediteur,
    avec_audio=False,
    avec_contenu=False
):
    """
    Texte de notification pour un message privé.
    """

    nom = nom_complet_utilisateur(expediteur)

    if avec_audio and avec_contenu:
        return (
            f"{nom} vous a envoyé un message "
            "avec un vocal."
        )

    if avec_audio:
        return (
            f"{nom} vous a envoyé "
            "un message vocal."
        )

    return (
        f"{nom} vous a envoyé "
        "un message."
    )


def texte_notification_groupe(
    expediteur,
    groupe,
    avec_audio=False,
    avec_contenu=False
):
    """
    Texte de notification pour un message de groupe.
    """

    nom = nom_complet_utilisateur(expediteur)

    if avec_audio and avec_contenu:
        return (
            f"{nom} a envoyé un message "
            f"avec un vocal dans « {groupe.nom} »."
        )

    if avec_audio:
        return (
            f"{nom} a envoyé un message vocal "
            f"dans « {groupe.nom} »."
        )

    return (
        f"{nom} a envoyé un message "
        f"dans « {groupe.nom} »."
    )


# =========================================================
# GROUPES DE L'UTILISATEUR
# =========================================================

def groupes_utilisateur(user):
    """
    Retourne les groupes actifs auxquels
    l'utilisateur appartient.

    Utilisation de MembreGroupe directement afin
    de ne pas dépendre du related_name du modèle Groupe.
    """

    groupe_ids = (
        MembreGroupe.objects
        .filter(
            utilisateur=user,
            actif=True
        )
        .values_list(
            "groupe_id",
            flat=True
        )
    )

    return (
        Groupe.objects
        .filter(
            id__in=groupe_ids,
            actif=True
        )
        .order_by("nom")
    )


# =========================================================
# CONVERSATIONS PRIVÉES
# =========================================================

def conversations_utilisateur(user):
    """
    Retourne les utilisateurs avec lesquels
    l'utilisateur possède une conversation.
    """

    messages_utilisateur = (
        Message.objects
        .filter(
            Q(expediteur=user)
            |
            Q(destinataire=user)
        )
        .select_related(
            "expediteur",
            "destinataire"
        )
        .order_by("-date_envoi")
    )

    utilisateurs_ids = set()

    for msg in messages_utilisateur:

        if msg.expediteur_id != user.id:
            utilisateurs_ids.add(
                msg.expediteur_id
            )

        if msg.destinataire_id != user.id:
            utilisateurs_ids.add(
                msg.destinataire_id
            )

    return (
        User.objects
        .filter(
            pk__in=utilisateurs_ids
        )
        .exclude(
            pk=user.pk
        )
        .order_by("username")
    )


# =========================================================
# COMPTEURS INDIVIDUELS
# =========================================================

def ajouter_compteurs_non_lus(
    request,
    utilisateurs_conversations,
    groupes
):
    """
    Ajoute les compteurs de messages non lus
    aux conversations privées et aux groupes.
    """

    # =====================================================
    # MESSAGES PRIVÉS NON LUS
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
    # MESSAGES GROUPES NON LUS
    # =====================================================

    for groupe in groupes:

        session_key = (
            f"messagerie_groupe_lu_{groupe.id}"
        )

        dernier_lu_id = request.session.get(
            session_key,
            0
        )

        try:
            dernier_lu_id = int(
                dernier_lu_id or 0
            )
        except (TypeError, ValueError):
            dernier_lu_id = 0

        groupe.messages_non_lus = (
            MessageGroupe.objects
            .filter(
                groupe=groupe,
                id__gt=dernier_lu_id
            )
            .exclude(
                expediteur=request.user
            )
            .count()
        )


# =========================================================
# NOTIFICATIONS
# =========================================================

def obtenir_notifications_non_lues(user):
    """
    Retourne les notifications non lues.
    """

    return (
        Notification.objects
        .filter(
            utilisateur=user,
            lue=False
        )
        .select_related(
            "expediteur",
            "message",
            "message_groupe",
            "message_groupe__groupe"
        )
        .order_by(
            "-date_creation"
        )
    )


# =========================================================
# MESSAGERIE PRINCIPALE
# =========================================================

@login_required
def boite_reception(
    request,
    utilisateur_id=None,
    groupe_id=None
):

    utilisateur_selectionne = None
    groupe_selectionne = None

    conversation = Message.objects.none()
    conversation_groupe = MessageGroupe.objects.none()

    # =====================================================
    # FORMULAIRES
    # =====================================================

    if request.method == "POST":

        type_message = request.POST.get(
            "type_message",
            ""
        )

        contenu = request.POST.get(
            "contenu",
            ""
        ).strip()

        audio = request.FILES.get(
            "audio"
        )

        # =================================================
        # MESSAGE PRIVÉ
        # =================================================

        if type_message == "individuel":

            destinataire_id = request.POST.get(
                "destinataire"
            )

            if (
                not destinataire_id
                or (
                    not contenu
                    and not audio
                )
            ):

                messages.error(
                    request,
                    "Veuillez saisir un message "
                    "ou enregistrer un message vocal."
                )

                if utilisateur_id:

                    return redirect(
                        "conversation",
                        utilisateur_id=utilisateur_id
                    )

                return redirect(
                    "boite_reception"
                )

            destinataire = get_object_or_404(
                User,
                pk=destinataire_id
            )

            # -------------------------------------------------
            # AUTO-ENVOI
            # -------------------------------------------------

            if destinataire.pk == request.user.pk:

                messages.error(
                    request,
                    "Vous ne pouvez pas vous envoyer "
                    "un message à vous-même."
                )

                return redirect(
                    "conversation",
                    utilisateur_id=destinataire.pk
                )

            # -------------------------------------------------
            # CRÉATION MESSAGE
            # -------------------------------------------------

            nouveau_message = Message.objects.create(
                expediteur=request.user,
                destinataire=destinataire,
                objet=(
                    "Message vocal"
                    if audio and not contenu
                    else "Message"
                ),
                contenu=contenu,
                audio=audio
            )

            # -------------------------------------------------
            # NOTIFICATION
            # -------------------------------------------------

            Notification.objects.create(
                utilisateur=destinataire,
                expediteur=request.user,
                message=nouveau_message,
                texte=texte_notification_prive(
                    request.user,
                    avec_audio=bool(audio),
                    avec_contenu=bool(contenu)
                )
            )

            # -------------------------------------------------
            # AJAX
            # -------------------------------------------------

            if est_ajax(request):

                return JsonResponse({
                    "success": True,
                    "redirect_url": (
                        f"/messagerie/conversation/"
                        f"{destinataire.pk}/"
                    )
                })

            return redirect(
                "conversation",
                utilisateur_id=destinataire.pk
            )

        # =================================================
        # MESSAGE GROUPE
        # =================================================

        elif type_message == "groupe":

            groupe_id_post = request.POST.get(
                "groupe_id"
            )

            if (
                not groupe_id_post
                or (
                    not contenu
                    and not audio
                )
            ):

                messages.error(
                    request,
                    "Veuillez saisir un message "
                    "ou enregistrer un message vocal."
                )

                if groupe_id:

                    return redirect(
                        "groupe_conversation",
                        groupe_id=groupe_id
                    )

                return redirect(
                    "boite_reception"
                )

            groupe = get_object_or_404(
                Groupe,
                pk=groupe_id_post,
                actif=True
            )

            # -------------------------------------------------
            # VÉRIFICATION APPARTENANCE
            # -------------------------------------------------

            membre = (
                MembreGroupe.objects
                .filter(
                    groupe=groupe,
                    utilisateur=request.user,
                    actif=True
                )
                .first()
            )

            if not membre:

                messages.error(
                    request,
                    "Vous ne faites pas partie "
                    "de ce groupe."
                )

                return redirect(
                    "boite_reception"
                )

            # -------------------------------------------------
            # CRÉATION MESSAGE
            # -------------------------------------------------

            nouveau_message = (
                MessageGroupe.objects.create(
                    groupe=groupe,
                    expediteur=request.user,
                    contenu=contenu,
                    audio=audio
                )
            )

            # -------------------------------------------------
            # NOTIFICATIONS
            # -------------------------------------------------

            membres = (
                MembreGroupe.objects
                .filter(
                    groupe=groupe,
                    actif=True
                )
                .exclude(
                    utilisateur=request.user
                )
                .select_related(
                    "utilisateur"
                )
            )

            texte_notification = (
                texte_notification_groupe(
                    request.user,
                    groupe,
                    avec_audio=bool(audio),
                    avec_contenu=bool(contenu)
                )
            )

            for membre_groupe in membres:

                Notification.objects.create(
                    utilisateur=(
                        membre_groupe.utilisateur
                    ),
                    expediteur=request.user,
                    message_groupe=nouveau_message,
                    texte=texte_notification
                )

            # -------------------------------------------------
            # EXPÉDITEUR = LU
            # -------------------------------------------------

            request.session[
                f"messagerie_groupe_lu_{groupe.id}"
            ] = nouveau_message.id

            request.session.modified = True

            # -------------------------------------------------
            # AJAX
            # -------------------------------------------------

            if est_ajax(request):

                return JsonResponse({
                    "success": True,
                    "redirect_url": (
                        f"/messagerie/groupe/"
                        f"{groupe.pk}/"
                    )
                })

            return redirect(
                "groupe_conversation",
                groupe_id=groupe.pk
            )

    # =====================================================
    # GROUPES
    # =====================================================

    groupes = groupes_utilisateur(
        request.user
    )

    # =====================================================
    # CONVERSATION PRIVÉE
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
                "expediteur",
                "destinataire"
            )
            .order_by("date_envoi")
        )

        # -------------------------------------------------
        # MARQUER LES MESSAGES COMME LUS
        # -------------------------------------------------

        Message.objects.filter(
            expediteur=utilisateur_selectionne,
            destinataire=request.user,
            lu=False
        ).update(
            lu=True
        )

        # -------------------------------------------------
        # NOTIFICATIONS LUES
        # -------------------------------------------------

        Notification.objects.filter(
            utilisateur=request.user,
            message__expediteur=utilisateur_selectionne,
            message__destinataire=request.user,
            lue=False
        ).update(
            lue=True
        )

    # =====================================================
    # CONVERSATION GROUPE
    # =====================================================

    elif groupe_id:

        groupe_selectionne = get_object_or_404(
            Groupe,
            pk=groupe_id,
            actif=True
        )

        membre = (
            MembreGroupe.objects
            .filter(
                groupe=groupe_selectionne,
                utilisateur=request.user,
                actif=True
            )
            .first()
        )

        if not membre:

            messages.error(
                request,
                "Vous n'avez pas accès à ce groupe."
            )

            return redirect(
                "boite_reception"
            )

        conversation_groupe = (
            MessageGroupe.objects
            .filter(
                groupe=groupe_selectionne
            )
            .select_related(
                "expediteur",
                "groupe"
            )
            .order_by("date_envoi")
        )

        # -------------------------------------------------
        # DERNIER MESSAGE
        # -------------------------------------------------

        dernier_message = (
            conversation_groupe
            .order_by("-id")
            .first()
        )

        if dernier_message:

            request.session[
                f"messagerie_groupe_lu_{groupe_selectionne.id}"
            ] = dernier_message.id

            request.session.modified = True

        # -------------------------------------------------
        # NOTIFICATIONS LUES
        # -------------------------------------------------

        Notification.objects.filter(
            utilisateur=request.user,
            message_groupe__groupe=groupe_selectionne,
            lue=False
        ).update(
            lue=True
        )

    # =====================================================
    # AUCUNE CONVERSATION
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
                "expediteur",
                "destinataire"
            )
            .order_by("-date_envoi")
            .first()
        )

        if derniere_activite:

            if (
                derniere_activite.expediteur_id
                == request.user.id
            ):

                autre_utilisateur_id = (
                    derniere_activite.destinataire_id
                )

            else:

                autre_utilisateur_id = (
                    derniere_activite.expediteur_id
                )

            return redirect(
                "conversation",
                utilisateur_id=autre_utilisateur_id
            )

        premier_groupe = groupes.first()

        if premier_groupe:

            return redirect(
                "groupe_conversation",
                groupe_id=premier_groupe.pk
            )

    # =====================================================
    # CONVERSATIONS PRIVÉES
    # =====================================================

    utilisateurs_conversations = (
        conversations_utilisateur(
            request.user
        )
    )

    # =====================================================
    # COMPTEURS INDIVIDUELS
    # =====================================================

    ajouter_compteurs_non_lus(
        request,
        utilisateurs_conversations,
        groupes
    )

    # =====================================================
    # TOUS LES UTILISATEURS
    # =====================================================

    utilisateurs = (
        User.objects
        .exclude(
            pk=request.user.pk
        )
        .order_by("username")
    )

    # =====================================================
    # MESSAGES PRIVÉS NON LUS
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
    # MESSAGES GROUPES NON LUS
    # =====================================================

    messages_groupes_non_lus = sum(
        getattr(
            groupe,
            "messages_non_lus",
            0
        )
        for groupe in groupes
    )

    # =====================================================
    # TOTAL DISCUSSIONS
    # =====================================================

    messages_non_lus = (
        messages_prives_non_lus
        +
        messages_groupes_non_lus
    )

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    notifications_non_lues = (
        obtenir_notifications_non_lues(
            request.user
        )
    )

    nombre_notifications = (
        notifications_non_lues.count()
    )

    # =====================================================
    # CONTEXTE
    # =====================================================

    context = {

        "utilisateur_selectionne":
            utilisateur_selectionne,

        "groupe_selectionne":
            groupe_selectionne,

        "conversation":
            conversation,

        "conversation_groupe":
            conversation_groupe,

        "utilisateurs_conversations":
            utilisateurs_conversations,

        "groupes":
            groupes,

        "utilisateurs":
            utilisateurs,

        # ---------------------------------------------
        # TOTAL MESSAGES NON LUS
        # ---------------------------------------------

        "messages_non_lus":
            messages_non_lus,

        # ---------------------------------------------
        # DÉTAILS
        # ---------------------------------------------

        "messages_prives_non_lus":
            messages_prives_non_lus,

        "messages_groupes_non_lus":
            messages_groupes_non_lus,

        # ---------------------------------------------
        # NOTIFICATIONS
        # ---------------------------------------------

        "notifications":
            notifications_non_lues,

        "notifications_non_lues":
            nombre_notifications,

        "nombre_notifications":
            nombre_notifications,
    }

    return render(
        request,
        "messagerie/boite_reception.html",
        context
    )


# =========================================================
# COMPTEUR GLOBAL DES MESSAGES NON LUS
# =========================================================

@login_required
def compteur_messages_non_lus(request):

    # =====================================================
    # MESSAGES PRIVÉS
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
    # GROUPES
    # =====================================================

    groupes = groupes_utilisateur(
        request.user
    )

    messages_groupes_non_lus = 0

    for groupe in groupes:

        session_key = (
            f"messagerie_groupe_lu_{groupe.id}"
        )

        dernier_lu_id = request.session.get(
            session_key,
            0
        )

        try:
            dernier_lu_id = int(
                dernier_lu_id or 0
            )
        except (TypeError, ValueError):

            dernier_lu_id = 0

        nombre = (
            MessageGroupe.objects
            .filter(
                groupe=groupe,
                id__gt=dernier_lu_id
            )
            .exclude(
                expediteur=request.user
            )
            .count()
        )

        messages_groupes_non_lus += nombre

    # =====================================================
    # TOTAL
    # =====================================================

    total_messages_non_lus = (
        messages_prives_non_lus
        +
        messages_groupes_non_lus
    )

    # =====================================================
    # RÉPONSE JSON
    # =====================================================

    return JsonResponse({

        "messages_non_lus":
            total_messages_non_lus,

        "messages_prives_non_lus":
            messages_prives_non_lus,

        "messages_groupes_non_lus":
            messages_groupes_non_lus,
    })


# =========================================================
# VÉRIFIER LES NOUVEAUX MESSAGES
# POUR LA SONNERIE
# =========================================================

@login_required
def verifier_nouveaux_messages(request):

    # =====================================================
    # DERNIER MESSAGE PRIVÉ REÇU
    # =====================================================

    dernier_prive = (
        Message.objects
        .filter(
            destinataire=request.user
        )
        .exclude(
            expediteur=request.user
        )
        .order_by("-id")
        .first()
    )

    dernier_prive_id = (
        dernier_prive.id
        if dernier_prive
        else 0
    )

    # =====================================================
    # GROUPES
    # =====================================================

    groupes = groupes_utilisateur(
        request.user
    )

    # =====================================================
    # DERNIER MESSAGE GROUPE REÇU
    # =====================================================

    dernier_groupe_id = 0

    for groupe in groupes:

        dernier = (
            MessageGroupe.objects
            .filter(
                groupe=groupe
            )
            .exclude(
                expediteur=request.user
            )
            .order_by("-id")
            .first()
        )

        if dernier:

            dernier_groupe_id = max(
                dernier_groupe_id,
                dernier.id
            )

    # =====================================================
    # CLÉS SESSION
    # =====================================================

    cle_prive = (
        "messagerie_dernier_prive_son"
    )

    cle_groupe = (
        "messagerie_dernier_groupe_son"
    )

    # =====================================================
    # PREMIÈRE VISITE
    # =====================================================

    if (
        cle_prive not in request.session
        or cle_groupe not in request.session
    ):

        request.session[cle_prive] = (
            dernier_prive_id
        )

        request.session[cle_groupe] = (
            dernier_groupe_id
        )

        request.session.modified = True

        return JsonResponse({

            "nouveau_message": False,

            "message_prive": False,

            "message_groupe": False,
        })

    # =====================================================
    # ANCIENS IDS
    # =====================================================

    try:

        ancien_prive_id = int(
            request.session.get(
                cle_prive,
                0
            ) or 0
        )

    except (TypeError, ValueError):

        ancien_prive_id = 0

    try:

        ancien_groupe_id = int(
            request.session.get(
                cle_groupe,
                0
            ) or 0
        )

    except (TypeError, ValueError):

        ancien_groupe_id = 0

    # =====================================================
    # DÉTECTION
    # =====================================================

    nouveau_prive = (
        dernier_prive_id
        >
        ancien_prive_id
    )

    nouveau_groupe = (
        dernier_groupe_id
        >
        ancien_groupe_id
    )

    nouveau_message = (
        nouveau_prive
        or
        nouveau_groupe
    )

    # =====================================================
    # MISE À JOUR SESSION
    # =====================================================

    if nouveau_prive:

        request.session[cle_prive] = (
            dernier_prive_id
        )

    if nouveau_groupe:

        request.session[cle_groupe] = (
            dernier_groupe_id
        )

    if nouveau_message:

        request.session.modified = True

    # =====================================================
    # RÉPONSE
    # =====================================================

    return JsonResponse({

        "nouveau_message":
            nouveau_message,

        "message_prive":
            nouveau_prive,

        "message_groupe":
            nouveau_groupe,
    })


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
            "expediteur",
            "destinataire"
        )
        .order_by("-date_envoi")
    )

    return render(
        request,
        "messagerie/messages_envoyes.html",
        {
            "messages_env":
                messages_env
        }
    )


# =========================================================
# NOUVELLE CONVERSATION
# =========================================================

@login_required
def nouveau_message(request):

    if request.method == "POST":

        destinataire_id = request.POST.get(
            "destinataire"
        )

        contenu = request.POST.get(
            "contenu",
            ""
        ).strip()

        audio = request.FILES.get(
            "audio"
        )

        if (
            not destinataire_id
            or (
                not contenu
                and not audio
            )
        ):

            messages.error(
                request,
                "Veuillez saisir un message "
                "ou enregistrer un message vocal."
            )

            return redirect(
                "nouveau_message"
            )

        destinataire = get_object_or_404(
            User,
            pk=destinataire_id
        )

        # -------------------------------------------------
        # AUTO-ENVOI
        # -------------------------------------------------

        if destinataire.pk == request.user.pk:

            messages.error(
                request,
                "Vous ne pouvez pas vous envoyer "
                "un message à vous-même."
            )

            return redirect(
                "nouveau_message"
            )

        # -------------------------------------------------
        # CRÉATION
        # -------------------------------------------------

        nouveau_message = Message.objects.create(
            expediteur=request.user,
            destinataire=destinataire,
            objet=(
                "Message vocal"
                if audio and not contenu
                else "Message"
            ),
            contenu=contenu,
            audio=audio
        )

        # -------------------------------------------------
        # NOTIFICATION
        # -------------------------------------------------

        Notification.objects.create(
            utilisateur=destinataire,
            expediteur=request.user,
            message=nouveau_message,
            texte=texte_notification_prive(
                request.user,
                avec_audio=bool(audio),
                avec_contenu=bool(contenu)
            )
        )

        return redirect(
            "conversation",
            utilisateur_id=destinataire.pk
        )

    # =====================================================
    # UTILISATEURS
    # =====================================================

    utilisateurs = (
        User.objects
        .exclude(
            pk=request.user.pk
        )
        .order_by("username")
    )

    return render(
        request,
        "messagerie/nouveau_message.html",
        {
            "utilisateurs":
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

    # =====================================================
    # MESSAGE LU
    # =====================================================

    if not message.lu:

        message.lu = True

        message.save(
            update_fields=["lu"]
        )

    # =====================================================
    # NOTIFICATION LUE
    # =====================================================

    Notification.objects.filter(
        utilisateur=request.user,
        message=message,
        lue=False
    ).update(
        lue=True
    )

    return render(
        request,
        "messagerie/lire_message.html",
        {
            "message":
                message
        }
    )


# =========================================================
# SUPPRIMER MESSAGE PRIVÉ
# =========================================================

@login_required
def supprimer_message(request, pk):

    message = get_object_or_404(
        Message,
        pk=pk,
        expediteur=request.user
    )

    if request.method != "POST":

        messages.error(
            request,
            "La suppression doit être effectuée par POST."
        )

        return redirect(
            "boite_reception"
        )

    destinataire_id = (
        message.destinataire_id
    )

    # -----------------------------------------------------
    # SUPPRIMER NOTIFICATION
    # -----------------------------------------------------

    Notification.objects.filter(
        message=message
    ).delete()

    # -----------------------------------------------------
    # SUPPRIMER MESSAGE
    # -----------------------------------------------------

    message.delete()

    # -----------------------------------------------------
    # AJAX
    # -----------------------------------------------------

    if est_ajax(request):

        return JsonResponse({
            "success": True
        })

    messages.success(
        request,
        "Message supprimé avec succès."
    )

    return redirect(
        "conversation",
        utilisateur_id=destinataire_id
    )


# =========================================================
# SUPPRIMER MESSAGE GROUPE
# =========================================================

@login_required
def supprimer_message_groupe(request, pk):

    message = get_object_or_404(
        MessageGroupe,
        pk=pk,
        expediteur=request.user
    )

    groupe_id = message.groupe_id

    # =====================================================
    # VÉRIFIER APPARTENANCE
    # =====================================================

    membre = (
        MembreGroupe.objects
        .filter(
            groupe_id=groupe_id,
            utilisateur=request.user,
            actif=True
        )
        .first()
    )

    if not membre:

        messages.error(
            request,
            "Vous n'avez pas accès à ce groupe."
        )

        return redirect(
            "boite_reception"
        )

    # =====================================================
    # POST
    # =====================================================

    if request.method != "POST":

        messages.error(
            request,
            "La suppression doit être effectuée par POST."
        )

        return redirect(
            "groupe_conversation",
            groupe_id=groupe_id
        )

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    Notification.objects.filter(
        message_groupe=message
    ).delete()

    # =====================================================
    # MESSAGE
    # =====================================================

    message.delete()

    # =====================================================
    # AJAX
    # =====================================================

    if est_ajax(request):

        return JsonResponse({
            "success": True
        })

    messages.success(
        request,
        "Message supprimé avec succès."
    )

    return redirect(
        "groupe_conversation",
        groupe_id=groupe_id
    )


# =========================================================
# CRÉER UN GROUPE
# =========================================================

@login_required
def creer_groupe(request):

    if request.method == "POST":

        nom = request.POST.get(
            "nom",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        membres_ids = request.POST.getlist(
            "membres"
        )

        # =================================================
        # VALIDATION
        # =================================================

        if not nom:

            messages.error(
                request,
                "Le nom du groupe est obligatoire."
            )

            return redirect(
                "creer_groupe"
            )

        # =================================================
        # CRÉER GROUPE
        # =================================================

        groupe = Groupe.objects.create(
            nom=nom,
            description=description,
            createur=request.user
        )

        # =================================================
        # CRÉATEUR = ADMINISTRATEUR
        # =================================================

        MembreGroupe.objects.create(
            groupe=groupe,
            utilisateur=request.user,
            administrateur=True
        )

        # =================================================
        # AJOUTER MEMBRES
        # =================================================

        for membre_id in membres_ids:

            if str(membre_id) == str(
                request.user.pk
            ):

                continue

            utilisateur = (
                User.objects
                .filter(
                    pk=membre_id
                )
                .first()
            )

            if utilisateur:

                MembreGroupe.objects.get_or_create(
                    groupe=groupe,
                    utilisateur=utilisateur
                )

        # =================================================
        # MESSAGE
        # =================================================

        messages.success(
            request,
            f"Le groupe « {groupe.nom} » "
            "a été créé avec succès."
        )

        return redirect(
            "groupe_conversation",
            groupe_id=groupe.pk
        )

    # =====================================================
    # UTILISATEURS
    # =====================================================

    utilisateurs = (
        User.objects
        .exclude(
            pk=request.user.pk
        )
        .order_by("username")
    )

    return render(
        request,
        "messagerie/groupe_creer.html",
        {
            "utilisateurs":
                utilisateurs
        }
    )


# =========================================================
# CONVERSATION GROUPE
# =========================================================

@login_required
def groupe_conversation(
    request,
    groupe_id
):

    groupe = get_object_or_404(
        Groupe,
        pk=groupe_id,
        actif=True
    )

    # =====================================================
    # VÉRIFIER MEMBRE
    # =====================================================

    membre = (
        MembreGroupe.objects
        .filter(
            groupe=groupe,
            utilisateur=request.user,
            actif=True
        )
        .first()
    )

    if not membre:

        messages.error(
            request,
            "Vous ne faites pas partie "
            "de ce groupe."
        )

        return redirect(
            "boite_reception"
        )

    # =====================================================
    # ENVOI MESSAGE
    # =====================================================

    if request.method == "POST":

        type_message = request.POST.get(
            "type_message",
            ""
        )

        contenu = request.POST.get(
            "contenu",
            ""
        ).strip()

        audio = request.FILES.get(
            "audio"
        )

        groupe_id_post = request.POST.get(
            "groupe_id"
        )

        if type_message == "groupe":

            # -------------------------------------------------
            # MESSAGE VIDE
            # -------------------------------------------------

            if (
                not contenu
                and not audio
            ):

                messages.error(
                    request,
                    "Le message ne peut pas être vide."
                )

                return redirect(
                    "groupe_conversation",
                    groupe_id=groupe.id
                )

            # -------------------------------------------------
            # VÉRIFIER GROUPE
            # -------------------------------------------------

            if str(groupe_id_post) != str(
                groupe.id
            ):

                messages.error(
                    request,
                    "Groupe invalide."
                )

                return redirect(
                    "groupe_conversation",
                    groupe_id=groupe.id
                )

            # -------------------------------------------------
            # CRÉATION
            # -------------------------------------------------

            nouveau_message = (
                MessageGroupe.objects.create(
                    groupe=groupe,
                    expediteur=request.user,
                    contenu=contenu,
                    audio=audio
                )
            )

            # -------------------------------------------------
            # MEMBRES
            # -------------------------------------------------

            membres = (
                MembreGroupe.objects
                .filter(
                    groupe=groupe,
                    actif=True
                )
                .exclude(
                    utilisateur=request.user
                )
                .select_related(
                    "utilisateur"
                )
            )

            # -------------------------------------------------
            # NOTIFICATION
            # -------------------------------------------------

            texte_notification = (
                texte_notification_groupe(
                    request.user,
                    groupe,
                    avec_audio=bool(audio),
                    avec_contenu=bool(contenu)
                )
            )

            for membre_groupe in membres:

                Notification.objects.create(
                    utilisateur=(
                        membre_groupe.utilisateur
                    ),
                    expediteur=request.user,
                    message_groupe=nouveau_message,
                    texte=texte_notification
                )

            # -------------------------------------------------
            # EXPÉDITEUR = LU
            # -------------------------------------------------

            request.session[
                f"messagerie_groupe_lu_{groupe.id}"
            ] = nouveau_message.id

            request.session.modified = True

            # -------------------------------------------------
            # AJAX
            # -------------------------------------------------

            if est_ajax(request):

                return JsonResponse({
                    "success": True,
                    "redirect_url": (
                        f"/messagerie/groupe/"
                        f"{groupe.id}/"
                    )
                })

            return redirect(
                "groupe_conversation",
                groupe_id=groupe.id
            )

    # =====================================================
    # MESSAGES
    # =====================================================

    conversation_groupe = (
        MessageGroupe.objects
        .filter(
            groupe=groupe
        )
        .select_related(
            "expediteur",
            "groupe"
        )
        .order_by("date_envoi")
    )

    # =====================================================
    # MARQUER COMME LU
    # =====================================================

    dernier_message = (
        conversation_groupe
        .order_by("-id")
        .first()
    )

    if dernier_message:

        request.session[
            f"messagerie_groupe_lu_{groupe.id}"
        ] = dernier_message.id

        request.session.modified = True

    # =====================================================
    # NOTIFICATIONS LUES
    # =====================================================

    Notification.objects.filter(
        utilisateur=request.user,
        message_groupe__groupe=groupe,
        lue=False
    ).update(
        lue=True
    )

    # =====================================================
    # GROUPES
    # =====================================================

    groupes = groupes_utilisateur(
        request.user
    )

    # =====================================================
    # CONVERSATIONS PRIVÉES
    # =====================================================

    utilisateurs_conversations = (
        conversations_utilisateur(
            request.user
        )
    )

    # =====================================================
    # COMPTEURS
    # =====================================================

    ajouter_compteurs_non_lus(
        request,
        utilisateurs_conversations,
        groupes
    )

    # =====================================================
    # TOUS LES UTILISATEURS
    # =====================================================

    utilisateurs = (
        User.objects
        .exclude(
            pk=request.user.pk
        )
        .order_by("username")
    )

    # =====================================================
    # PRIVÉS NON LUS
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
    # GROUPES NON LUS
    # =====================================================

    messages_groupes_non_lus = sum(
        getattr(
            groupe_item,
            "messages_non_lus",
            0
        )
        for groupe_item in groupes
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
    # NOTIFICATIONS
    # =====================================================

    notifications_non_lues = (
        obtenir_notifications_non_lues(
            request.user
        )
    )

    nombre_notifications = (
        notifications_non_lues.count()
    )

    # =====================================================
    # CONTEXTE
    # =====================================================

    context = {

        "utilisateur_selectionne":
            None,

        "groupe_selectionne":
            groupe,

        "conversation":
            Message.objects.none(),

        "conversation_groupe":
            conversation_groupe,

        "utilisateurs_conversations":
            utilisateurs_conversations,

        "groupes":
            groupes,

        "utilisateurs":
            utilisateurs,

        "messages_non_lus":
            messages_non_lus,

        "messages_prives_non_lus":
            messages_prives_non_lus,

        "messages_groupes_non_lus":
            messages_groupes_non_lus,

        "notifications":
            notifications_non_lues,

        "notifications_non_lues":
            nombre_notifications,

        "nombre_notifications":
            nombre_notifications,
    }

    return render(
        request,
        "messagerie/boite_reception.html",
        context
    )
# messagerie/context_processors.py

from django.db.models import Q

from .models import Message, Groupe, MessageGroupe


def messagerie_context(request):

    # =====================================================
    # UTILISATEUR NON CONNECTÉ
    # =====================================================

    if not request.user.is_authenticated:
        return {
            'messages_non_lus': 0,
        }


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
    )


    # =====================================================
    # MESSAGES DE GROUPES NON LUS
    # =====================================================

    messages_groupes_non_lus = 0


    for groupe in groupes:

        # ID du dernier message consulté
        session_key = (
            f'messagerie_groupe_lu_{groupe.id}'
        )

        dernier_message_lu_id = (
            request.session.get(
                session_key,
                0
            )
        )

        # Nombre de messages arrivés depuis
        # le dernier message consulté
        messages_groupes_non_lus += (
            MessageGroupe.objects
            .filter(
                groupe=groupe,
                id__gt=dernier_message_lu_id
            )
            .exclude(
                expediteur=request.user
            )
            .count()
        )


    # =====================================================
    # TOTAL
    # =====================================================

    total_non_lus = (
        messages_prives_non_lus
        +
        messages_groupes_non_lus
    )


    return {
        'messages_non_lus': total_non_lus,
        'messages_prives_non_lus': messages_prives_non_lus,
        'messages_groupes_non_lus': messages_groupes_non_lus,
    }
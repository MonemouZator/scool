
from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # MESSAGERIE PRINCIPALE
    # =====================================================

    path(
        '',
        views.boite_reception,
        name='boite_reception'
    ),

    # =====================================================
    # CONVERSATION INDIVIDUELLE
    # =====================================================

    path(
        'conversation/<int:utilisateur_id>/',
        views.boite_reception,
        name='conversation'
    ),

    # =====================================================
    # CONVERSATION GROUPE
    # =====================================================

    path(
        'groupe/<int:groupe_id>/',
        views.groupe_conversation,
        name='groupe_conversation'
    ),

    # =====================================================
    # NOUVEAU MESSAGE
    # =====================================================

    path(
        'nouveau/',
        views.nouveau_message,
        name='nouveau_message'
    ),

    # =====================================================
    # CRÉER UN GROUPE
    # =====================================================

    path(
        'groupe/creer/',
        views.creer_groupe,
        name='creer_groupe'
    ),

    # =====================================================
    # MESSAGES ENVOYÉS
    # =====================================================

    path(
        'envoyes/',
        views.messages_envoyes,
        name='messages_envoyes'
    ),

    # =====================================================
    # LIRE UN MESSAGE
    # =====================================================

    path(
        'lire/<int:pk>/',
        views.lire_message,
        name='lire_message'
    ),

    # =====================================================
    # SUPPRIMER UN MESSAGE INDIVIDUEL
    # =====================================================

    path(
        'supprimer/<int:pk>/',
        views.supprimer_message,
        name='supprimer_message'
    ),

    # =====================================================
    # SUPPRIMER UN MESSAGE GROUPE
    # =====================================================

    path(
        'groupe/message/supprimer/<int:pk>/',
        views.supprimer_message_groupe,
        name='supprimer_message_groupe'
    ),

    # =====================================================
    # COMPTEUR DES MESSAGES NON LUS
    # =====================================================

    path(
        'compteur-messages/',
        views.compteur_messages_non_lus,
        name='compteur_messages_non_lus'
    ),

    # =====================================================
    # VÉRIFIER LES NOUVEAUX MESSAGES
    # =====================================================

    path(
        'verifier-nouveaux-messages/',
        views.verifier_nouveaux_messages,
        name='verifier_nouveaux_messages'
    ),
]

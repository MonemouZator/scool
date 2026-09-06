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
    # LIRE
    # =====================================================

    path(
        'lire/<int:pk>/',
        views.lire_message,
        name='lire_message'
    ),

    # =====================================================
    # SUPPRIMER
    # =====================================================

    path(
        'supprimer/<int:pk>/',
        views.supprimer_message,
        name='supprimer_message'
    ),
]
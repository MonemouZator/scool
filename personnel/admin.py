
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Administrateur, Historique, Token


# ==============================================================
# ADMINISTRATEUR
# ==============================================================

@admin.register(Administrateur)
class AdministrateurAdmin(UserAdmin):

    # ==========================================================
    # LISTE DES UTILISATEURS
    # ==========================================================
    list_display = (
        'username',
        'nom',
        'prenom',
        'email',
        'telephone',
        'fonction',
        'genre',
        'date_naissance',
        'lieu_naiss',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    # ==========================================================
    # FILTRES
    # ==========================================================
    list_filter = (
        'fonction',
        'genre',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    # ==========================================================
    # RECHERCHE
    # ==========================================================
    search_fields = (
        'username',
        'nom',
        'prenom',
        'email',
        'telephone',
        'lieu_naiss',
    )

    # ==========================================================
    # TRI
    # ==========================================================
    ordering = (
        'nom',
        'prenom',
    )

    # ==========================================================
    # LIENS CLIQUABLES
    # ==========================================================
    list_display_links = (
        'username',
        'nom',
        'prenom',
    )

    # ==========================================================
    # MODIFICATION DIRECTE
    # ==========================================================
    list_editable = (
        'fonction',
        'is_active',
        'is_staff',
    )

    # ==========================================================
    # FORMULAIRE DE MODIFICATION
    # ==========================================================
    fieldsets = (
        (
            'Informations de connexion',
            {
                'fields': (
                    'username',
                    'password',
                )
            }
        ),

        (
            'Informations personnelles',
            {
                'fields': (
                    'nom',
                    'prenom',
                    'email',
                    'telephone',
                    'genre',
                    'date_naissance',
                    'lieu_naiss',
                    'fonction',
                    'photo',
                )
            }
        ),

        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            }
        ),

        (
            'Dates',
            {
                'fields': (
                    'last_login',
                    'date_joined',
                )
            }
        ),
    )

    # ==========================================================
    # FORMULAIRE DE CRÉATION
    # ==========================================================
    add_fieldsets = (
        (
            'Création du compte',
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'password1',
                    'password2',
                    'email',
                ),
            }
        ),

        (
            'Informations personnelles',
            {
                'classes': ('wide',),
                'fields': (
                    'nom',
                    'prenom',
                    'telephone',
                    'genre',
                    'date_naissance',
                    'lieu_naiss',
                    'fonction',
                    'photo',
                ),
            }
        ),

        (
            'Permissions',
            {
                'classes': ('wide',),
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            }
        ),
    )

    # ==========================================================
    # CHAMPS EN LECTURE SEULE
    # ==========================================================
    readonly_fields = (
        'last_login',
        'date_joined',
    )


# ==============================================================
# HISTORIQUE
# ==============================================================

@admin.register(Historique)
class HistoriqueAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'action',
        'created_time',
    )

    search_fields = (
        'user__username',
        'user__nom',
        'user__prenom',
        'action',
    )

    list_filter = (
        'created_time',
    )

    ordering = (
        '-created_time',
    )

    readonly_fields = (
        'created_time',
    )


# ==============================================================
# TOKEN
# ==============================================================

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'token',
    )

    search_fields = (
        'user__username',
        'user__email',
        'token',
    )

    ordering = (
        'user',
    )


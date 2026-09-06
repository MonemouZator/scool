from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'expediteur',
        'destinataire',
        'objet',
        'date_envoi',
        'lu',
    )

    list_filter = (
        'lu',
        'date_envoi',
    )

    search_fields = (
        'objet',
        'contenu',
        'expediteur__username',
        'destinataire__username',
    )

    readonly_fields = (
        'date_envoi',
    )
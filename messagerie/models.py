from django.conf import settings
from django.db import models


# =========================================================
# MESSAGE INDIVIDUEL
# =========================================================

class Message(models.Model):

    expediteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_envoyes'
    )

    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_recus'
    )

    objet = models.CharField(
        max_length=255
    )

    contenu = models.TextField()

    date_envoi = models.DateTimeField(
        auto_now_add=True
    )

    lu = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.expediteur} → {self.destinataire} : {self.objet}"

    class Meta:
        ordering = ['-date_envoi']
        verbose_name = "Message"
        verbose_name_plural = "Messages"


# =========================================================
# GROUPE DE DISCUSSION
# =========================================================

class Groupe(models.Model):

    nom = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='groupes_crees'
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    actif = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"


# =========================================================
# MEMBRES D'UN GROUPE
# =========================================================

class MembreGroupe(models.Model):

    groupe = models.ForeignKey(
        Groupe,
        on_delete=models.CASCADE,
        related_name='membres'
    )

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participations_groupes'
    )

    date_adhesion = models.DateTimeField(
        auto_now_add=True
    )

    administrateur = models.BooleanField(
        default=False
    )

    actif = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.utilisateur} - {self.groupe}"

    class Meta:
        ordering = ['date_adhesion']
        verbose_name = "Membre du groupe"
        verbose_name_plural = "Membres des groupes"

        constraints = [
            models.UniqueConstraint(
                fields=['groupe', 'utilisateur'],
                name='unique_membre_groupe'
            )
        ]


# =========================================================
# MESSAGE DE GROUPE
# =========================================================

class MessageGroupe(models.Model):

    groupe = models.ForeignKey(
        Groupe,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    expediteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_groupes_envoyes'
    )

    contenu = models.TextField()

    date_envoi = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.expediteur} → {self.groupe}: {self.contenu[:40]}"

    class Meta:
        ordering = ['date_envoi']
        verbose_name = "Message de groupe"
        verbose_name_plural = "Messages de groupe"
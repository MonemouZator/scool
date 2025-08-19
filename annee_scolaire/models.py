from django.db import models
from datetime import date

# Année Scolaire
class AnneeScolaire(models.Model):
    nom = models.CharField(max_length=9, unique=True)  # Exemple : "2023-2024"
    date_debut = models.DateField()
    date_fin = models.DateField()

    # Assurer que la date_debut est avant date_fin
    def save(self, *args, **kwargs):
        if self.date_debut > self.date_fin:
            raise ValueError("La date de début doit être avant la date de fin.")
        super(AnneeScolaire, self).save(*args, **kwargs)

    # Méthode pour vérifier si l'année scolaire est en cours
    def en_cours(self):
        today = date.today()
        return self.date_debut <= today <= self.date_fin

    def __str__(self):
        return self.nom
    class Meta:

        ordering=['-nom']

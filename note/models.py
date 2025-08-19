from django.db import models

from eleve.models import Eleve

from matiere.models import Matiere

from annee_scolaire.models import AnneeScolaire

class Note(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    note_cours = models.FloatField()
    note_comp = models.FloatField()
    trimestre = models.PositiveIntegerField()  # Cela devrait être un entier
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)

    @property
    def moyenne(self):
        return round((self.note_comp + self.note_cours) / 2, 2)

    def __str__(self):
        return f"{self.eleve} - {self.matiere}"

    class Meta:
        ordering=['-id']


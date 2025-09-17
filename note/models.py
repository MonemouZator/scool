from django.db import models

from eleve.models import Eleve

from matiere.models import Matiere

from annee_scolaire.models import AnneeScolaire

class Note(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    note_cours = models.FloatField(null=True, blank=True)
    note_comp = models.FloatField(null=True, blank=True)
    note_finale = models.FloatField(null=True, blank=True)
    trimestre = models.PositiveIntegerField()
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']
        unique_together = ('eleve', 'matiere', 'trimestre', 'annee_scolaire')

    @property
    def moyenne(self):
        if self.note_cours is not None and self.note_comp is not None:
            return round((self.note_cours + self.note_comp) / 2, 2)
        return None

    def save(self, *args, **kwargs):
        if self.note_cours is not None and self.note_comp is not None:
            self.note_finale = self.moyenne
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.eleve} - {self.matiere} | Moyenne: {self.moyenne}"

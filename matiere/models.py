from django.db import models
from niveau.models import Niveau
from groupe_classe.models import GroupeClasse

# Matière
class Matiere(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    coefficient = models.FloatField()
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom
    
    class Meta:
        ordering = ['-id']

# Relation Enseignant-Matière
class EnseignantMatiere(models.Model):
    enseignant = models.ForeignKey('enseignant.Enseignant', on_delete=models.CASCADE)  # chaîne de caractères
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    groupe_classe = models.ForeignKey(GroupeClasse, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('enseignant', 'matiere', 'niveau', 'groupe_classe')

    def __str__(self):
        return f"{self.enseignant} - {self.matiere} ({self.niveau}-{self.groupe_classe})"

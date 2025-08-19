from django.db import models
from niveau.models import Niveau

# Groupe Classe
class GroupeClasse(models.Model):
    nom = models.CharField(max_length=50,db_index=False)  # Exemple : "6A", "1B"
    niveau = models.ForeignKey(Niveau , on_delete=models.CASCADE)

    def __str__(self):
        return f" {self.nom} "
    
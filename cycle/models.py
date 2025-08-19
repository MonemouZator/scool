from django.db import models

class Cycle(models.Model):
    nom = models.CharField(max_length=30,db_index=False ,unique=True)  # Exemple : "Primaire", "Secondaire"
    description = models.TextField(blank=True, null=True,db_index=False)

    def __str__(self):
        return self.nom

from django.db import models
from cloudinary.models import CloudinaryField

class Cycle(models.Model):
    nom = models.CharField(max_length=30,db_index=False ,unique=True)  # Exemple : "Primaire", "Secondaire"
    description = models.TextField(blank=True, null=True,db_index=False)

    def __str__(self):
        return self.nom


class Etablissement(models.Model):

    nom_ecole = models.CharField(max_length=30,db_index=False ,unique=True)
    devise_ecole = models.CharField(max_length=30,db_index=False)
    pays = models.CharField(max_length=30,db_index=False)
    devise_pays = models.CharField(max_length=30,db_index=False)
    meapu = models.CharField(max_length=30,db_index=False)
    ire = models.CharField(max_length=30,db_index=False)
    dpe = models.CharField(max_length=30,db_index=False)
    dsee = models.CharField(max_length=30,db_index=False)
    date_creation=models.DateField()
    logo = CloudinaryField('image', blank=True, null=True, overwrite=True)
    responsable=models.CharField(max_length=50)
    def __str__(self):

        return self.nom_ecole
 
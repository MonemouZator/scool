from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

class Administrateur(AbstractUser):
    TYPE = [
        ('FONDATEUR', 'PDG'),
        ('DG', "DIRECTEUR D'ECOLE"),
        ('CENSEUR', "CENSEUR D'ECOLE"),
        ('COMPTABLE', "GESTIONAIRE DE LA FINANCE"),
        ('ENSEIGNANT', "GESTIONAIRE DES NOTES"),
        ('PROVISEUR', "PROVISEUR DE L'ECOLE"),
    ]
    
    
    nom = models.CharField(max_length=40, db_index=True)  # Indexé pour de meilleures performances
    prenom = models.CharField(max_length=40, db_index=True)
    telephone = models.CharField(max_length=15, db_index=True, unique=True)  # Unicité recommandée
    genre = models.CharField(max_length=15)
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naiss = models.CharField(max_length=30, db_index=True)
    fonction = models.CharField(max_length=256, choices=TYPE, null=True)
    photo = CloudinaryField('image', blank=True, null=True, overwrite=True)
  # Dossier de stockage
    email = models.EmailField(max_length=191, unique=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.fonction}"

class Historique(models.Model):
    user=models.ForeignKey(Administrateur,on_delete=models.CASCADE)
    action=models.CharField(max_length=3096)
    created_time=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {self.created_time}"
    
class Token(models.Model):
    user=models.ForeignKey(Administrateur,on_delete=models.CASCADE)
    token=models.CharField(max_length=256)


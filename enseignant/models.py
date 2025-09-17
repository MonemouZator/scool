from django.db import models
from matiere.models import Matiere
from django.utils import timezone
from groupe_classe.models import GroupeClasse
from niveau.models import Niveau

from annee_scolaire.models import AnneeScolaire
from cloudinary.models import CloudinaryField



from django.conf import settings

class Enseignant(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='enseignant_profile'
    )
    nom = models.CharField(max_length=40)
    prenom = models.CharField(max_length=40)
    specialite = models.CharField(max_length=40)
    telephone = models.CharField(max_length=15)
    sexe = models.CharField(max_length=10, choices=[("Homme", "Masculin"), ("Femme", "Feminin")])
    adresse = models.CharField(max_length=60)
    date_naiss = models.DateField()
    lieu_naiss = models.CharField(max_length=30)
    photo = CloudinaryField('image', blank=True, null=True, overwrite=True)
    email = models.EmailField(max_length=254)

    class Meta:
        unique_together = ('nom', 'prenom')

    def __str__(self):
        return f"{self.nom} {self.prenom}"
    

class PaiementSalaire(models.Model):
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField(default=timezone.now)
    statut = models.CharField(max_length=20, choices=[('Payé', 'Payé'), ('Non Payé', 'Non Payé')], default='Non Payé')
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)  # Relation avec l'année scolaire
    def __str__(self):
        return f"Paiement de {self.montant} pour {self.enseignant.nom} {self.enseignant.prenom} ({self.statut})"
    
class Depense(models.Model):
    CATEGORIES_DEPENSES = [
        ('Matériel', 'Matériel'),
        ('Électricité', 'Électricité'),
        ('Eau', 'Eau'),
        ('Maintenance', 'Maintenance'),
        ('Autre', 'Autre'),
    ]
    
    description = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_depense = models.DateField(default=timezone.now)
    categorie = models.CharField(max_length=50, choices=CATEGORIES_DEPENSES, default='Autre')
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)  # Relation avec l'année scolaire
    def __str__(self):
        return f"{self.description} - {self.montant} GNF ({self.categorie})"
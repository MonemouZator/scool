from django.db import models

from niveau.models import Niveau

from groupe_classe.models import GroupeClasse

from annee_scolaire.models import AnneeScolaire

from django.utils import timezone

from cloudinary.models import CloudinaryField

from django.db import models
from niveau.models import Niveau
from groupe_classe.models import GroupeClasse
from annee_scolaire.models import AnneeScolaire

class Eleve(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    groupe_classe = models.ForeignKey(GroupeClasse, on_delete=models.CASCADE)
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.TextField()
    genre = models.CharField(max_length=15)
    telephone = models.CharField(max_length=15,null=True,blank=True)
    photo = CloudinaryField('image', blank=True, null=True, overwrite=True)

    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True)
    niveau = models.ForeignKey(Niveau, on_delete=models.SET_NULL, null=True, blank=True)
    
    pere = models.CharField(max_length=191)
    profession_pere = models.CharField(max_length=191)
    contact_parent = models.CharField(max_length=15, null=True, blank=True)
    mere = models.CharField(max_length=191)
    profession_mere = models.CharField(max_length=191)
    contact_mere = models.CharField(max_length=15, null=True, blank=True)
    
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.niveau and self.annee_scolaire:
            montant_total = self.niveau.montant_frais or 0
            frais_existe = FraisScolarite.objects.filter(eleve=self, annee_scolaire=self.annee_scolaire).exists()

            if not frais_existe:
                # Créer les frais pour l'élève sans diviser en trois tranches
                FraisScolarite.objects.create(
                eleve=self,
                annee_scolaire=self.annee_scolaire,
                montant_total=montant_total,
                tranche1=0,
                tranche2=0,
                tranche3=0,
                total_paye=0,
                solde=montant_total,
                est_paye=False
            )


# Assurez-vous d'avoir le modèle Recu défini auparavant pour ce code à fonctionner
class FraisScolarite(models.Model):
    eleve = models.ForeignKey('Eleve', on_delete=models.CASCADE, related_name='frais_scolarites')
    annee_scolaire = models.ForeignKey('annee_scolaire.AnneeScolaire', on_delete=models.CASCADE)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    total_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Gestion des trois tranches
    tranche1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tranche2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tranche3 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    est_paye = models.BooleanField(default=False)  # Pour savoir si le paiement est effectué

    def __str__(self):
        return f"Frais pour {self.eleve.nom} {self.eleve.prenom}"

    def save(self, *args, **kwargs):
        # Met à jour le solde restant
        self.solde = self.montant_total - self.total_paye
        super().save(*args, **kwargs)

    def enregistrer_paiement(self, montant, tranche):
        # Création du reçu
        recu = Recu.objects.create(
            frais_scolarite=self,
            montant=montant,
            details=f"Paiement pour {self.eleve.nom} {self.eleve.prenom} - Tranche {tranche}."
        )

        # Appliquer le paiement à la bonne tranche
        if tranche == 1:
            self.tranche1 += montant
        elif tranche == 2:
            self.tranche2 += montant
        elif tranche == 3:
            self.tranche3 += montant
        self.total_paye += montant  # Mettre à jour le total payé
        self.solde = self.montant_total - self.total_paye  # Mettre à jour le solde restant

        # Vérifie si l'élève a payé intégralement
        if self.total_paye >= self.montant_total:
            self.est_paye = True

        self.save()  # Sauvegarder les changements dans FraisScolarite
        return recu  # Retourne le reçu créé


    
class Recu(models.Model):
    frais_scolarite = models.ForeignKey(FraisScolarite, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_recu = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"Reçu {self.id} - {self.frais_scolarite.eleve.nom} {self.frais_scolarite.eleve.prenom}"
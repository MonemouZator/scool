from django.db import models

from niveau.models import Niveau

from groupe_classe.models import GroupeClasse

from annee_scolaire.models import AnneeScolaire

from django.utils import timezone

from cloudinary.models import CloudinaryField
import random
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
    

# ✅ Nouveau champ matricule
    matricule = models.CharField(max_length=20, unique=True, blank=True, null=True)
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    # 🔹 Méthode pour générer un matricule unique
    def generate_matricule(self):
        nom_part = (self.nom[:2] if len(self.nom) >= 2 else self.nom).upper()
        prenom_part = (self.prenom[:2] if len(self.prenom) >= 2 else self.prenom).upper()
       
        # Vérifier que date_naissance existe
        annee = self.date_naissance.year if self.date_naissance else '0000'
        matricule_base = f"{nom_part}{prenom_part}{annee}"
       
        # Ajouter un suffixe aléatoire pour garantir l'unicité
        suffixe = ''.join([str(random.randint(0,9)) for _ in range(2)])
        matricule = f"{matricule_base}{suffixe}"
        # Vérifier unicité
        while Eleve.objects.filter(matricule=matricule).exists():
            suffixe = ''.join([str(random.randint(0,9)) for _ in range(2)])
            matricule = f"{matricule_base}{suffixe}"
        return matricule
    # 🔹 Sauvegarde avec matricule automatique
    def save(self, *args, **kwargs):
        if not self.matricule:
            self.matricule = self.generate_matricule()

        # IMPORTANT :
        # super().save() doit être exécuté à chaque modification,
        # sinon les modifications (nom, photo, téléphone, etc.) ne sont pas enregistrées.
        super().save(*args, **kwargs)

        # Création automatique des frais scolaires
        if self.niveau and self.annee_scolaire:
            montant_total = self.niveau.montant_frais or 0

            frais_existe = FraisScolarite.objects.filter(
                eleve=self,
                annee_scolaire=self.annee_scolaire
            ).exists()

            if not frais_existe:
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

class EleveInscrit(models.Model):
    eleve = models.ForeignKey('Eleve', on_delete=models.CASCADE, related_name="inscriptions")
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    groupe_classe = models.ForeignKey(GroupeClasse, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveau, on_delete=models.SET_NULL, null=True, blank=True)
    actif = models.BooleanField(default=True)  # Pour savoir si l'élève est actuellement inscrit
    date_inscription = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('eleve', 'annee_scolaire')  # un élève ne peut être inscrit qu'une fois par année
    def __str__(self):
        return f"{self.eleve.prenom} {self.eleve.nom} - {self.annee_scolaire.nom}"   
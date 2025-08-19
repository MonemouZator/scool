from django.db import models
from eleve.models import Eleve
from annee_scolaire.models import AnneeScolaire
from note.models import Note
from django.db.models import Avg, F


class BulletinTrimestriel(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    trimestre = models.PositiveIntegerField()
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)

    from django.db.models import Avg, F

    @property
    def notes_par_matiere(self):
        # Calcul des moyennes des matières pour le trimestre sélectionné
        notes = Note.objects.filter(
            eleve=self.eleve,
            trimestre=self.trimestre,
            annee_scolaire=self.annee_scolaire
        ).values('matiere__nom').annotate(
            moyenne_matiere=Avg((F('note_cours') + F('note_comp')) / 2)
        )
        return list(notes)  # Convertir en liste pour être utilisée dans le template


    @property
    def moyenne_totale(self):
        # Calcul de la moyenne totale du trimestre
        notes = Note.objects.filter(
            eleve=self.eleve,
            trimestre=self.trimestre,
            annee_scolaire=self.annee_scolaire
        )
        moyenne_totale = notes.aggregate(
            moyenne_semestre=Avg(F('note_cours') + F('note_comp')) / 2
        )['moyenne_semestre']
        return round(moyenne_totale, 2) if moyenne_totale else None

    def __str__(self):
        return f"Bulletin Trimestriel - {self.eleve.nom} - Trimestre {self.trimestre}"


    def get_rang(self):
        # Calcul du rang de l'élève par rapport aux autres dans le même trimestre et année scolaire
        bulletins_trimestriels = BulletinTrimestriel.objects.filter(
            annee_scolaire=self.annee_scolaire,
            trimestre=self.trimestre
        )
        # Crée une liste de tuples (élève, moyenne totale) pour chaque bulletin
        moyennes = [(b.eleve, b.moyenne_totale) for b in bulletins_trimestriels]
        # Trie les élèves par leur moyenne totale décroissante
        moyennes_triees = sorted(moyennes, key=lambda x: x[1], reverse=True)
        # Recherche le rang de l'élève actuel
        rang = next(index for index, (e, _) in enumerate(moyennes_triees) if e == self.eleve) + 1
        return rang
    
#BULLETIN ANNUEL
class BulletinAnnuel(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    observation = models.TextField(blank=True, null=True)

    @property
    def moyenne_totale_par_trimestre(self):
        # Calcul des moyennes pour les deux trimestres
        moyenne_t1 = Note.objects.filter(
            eleve=self.eleve,
            annee_scolaire=self.annee_scolaire,
            trimestre=1
        ).aggregate(moyenne_t1=Avg(F('note_cours') + F('note_comp')))['moyenne_t1'] or 0

        moyenne_t2 = Note.objects.filter(
            eleve=self.eleve,
            annee_scolaire=self.annee_scolaire,
            trimestre=2
        ).aggregate(moyenne_t2=Avg(F('note_cours') + F('note_comp')))['moyenne_t2'] or 0

        moyenne_t3 = Note.objects.filter(
            eleve=self.eleve,
            annee_scolaire=self.annee_scolaire,
            trimestre=3
        ).aggregate(moyenne_t3=Avg(F('note_cours') + F('note_comp')))['moyenne_t3'] or 0


        return {
            'moyenne_t1': round(moyenne_t1 / 2, 2),
            'moyenne_t2': round(moyenne_t2 / 2, 2),
            'moyenne_t3': round(moyenne_t3 / 2, 2),
        }

    @property
    def moyenne_totale_annuelle(self):
        # Calcul de la moyenne annuelle en fonction des deux trimestres
        moyennes = self.moyenne_totale_par_trimestre
        total_moyennes = moyennes['moyenne_t1'] + moyennes['moyenne_t2'] + moyennes['moyenne_t3']
        return round(total_moyennes / 3, 2)

    def get_rang(self):
        # Calcul du rang de l'élève par rapport aux autres dans le même groupe
        bulletins_annuels = BulletinAnnuel.objects.filter(annee_scolaire=self.annee_scolaire)
        moyennes = [(b.eleve, b.moyenne_totale_annuelle) for b in bulletins_annuels]
        moyennes_triees = sorted(moyennes, key=lambda x: x[1], reverse=True)
        rang = next(index for index, (e, _) in enumerate(moyennes_triees) if e == self.eleve) + 1
        return rang

    def __str__(self):
        return f"Bulletin Annuel - {self.eleve.nom} - {self.annee_scolaire.nom}"
